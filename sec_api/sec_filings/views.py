"""Views that exposes APIs"""

import json
import logging

from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt

from sec_api import asgi
from sec_filings.models import NonDerivative, Owner, Company

from collections import defaultdict


logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


@csrf_exempt
def new_feed(request):
    """Signals that new data is in the feed."""

    asgi.channel_layer.send(
        channel='websocket.new_message',
        message={
            'reply_channel': 'websocket.new_message',
            'text': 'New Message',
            'path': '/feed/'
        }
    )

    return HttpResponse(
        json.dumps(['Message Received'], cls=DjangoJSONEncoder),
        content_type='application/json',
        status=200
    )


def get_feed(request):
    nonderivatives = NonDerivative.objects\
        .order_by('-datetime')[:20]\
        .prefetch_related('issuer', 'owner')

    payload = {}

    for nd in nonderivatives:

        company = nd.issuer.name
        owner = nd.owner.name

        data = dict(
            id=nd.id,
            datetime=nd.datetime,
            security=nd.security,
            shares=nd.shares,
            is_acquisition=1 if nd.acqdisp_code == 'A' else 0,
            pricepershare=nd.pricepershare,
            ownershipnature=nd.ownershipnature,
            owner_sharesownedfollowingtransaction=\
                nd.owner_sharesownedfollowingtransaction,
            accession_num=nd.accession_num
        )

        if company not in payload:
            payload[company] = {owner: []}

        # Create owner if the entity isn't already catalogued.
        try:
            payload[company][owner].append(data)
        except KeyError:
            payload[company][owner] = [data]


    payload = {
        'companies': [{
            _comp : {
                'owners': [{
                    _owner: _transactions
                } for _owner, _transactions in _val.items()]
            }
        } for _comp, _val in payload.items()]
    }


    return HttpResponse(
        json.dumps(payload, cls=DjangoJSONEncoder),
        content_type='application/json',
        status=200
    )


@csrf_exempt
def get_accessionnums(request):
    """Gets nonderivatives accessionsnums that are storred in MySQL."""

    accession_nums = NonDerivative.objects.values('accession_num').distinct()

    return HttpResponse(
        json.dumps(
            [row['accession_num'] for row in accession_nums],
            cls=DjangoJSONEncoder
        ),
        content_type='application/json',
        status=200
    )


@csrf_exempt
def nonderivative(request):

    message = []

    datums = json.loads(request.body)

    for datum in datums:

        owner_cik = datum['owner_cik']
        issuer_cik = datum['issuer_cik']

        owner_kwargs = dict(
            name=datum['owner_name'],
            isdirector=datum['owner_isdirector'],
            isofficer=datum['owner_isofficer'],
            officertitle=datum['owner_officertitle'],
            street1=datum['owner_street1'],
            street2=datum['owner_street2'],
            city=datum['owner_city'],
            state=datum['owner_state'],
            zipcode=datum['owner_zip'],
        )

        owner, _ = Owner.objects.update_or_create(
            cik=owner_cik,
            defaults=owner_kwargs
        )

        issuer_kwargs = dict(
            name=datum['issuer_name'],
            ticker=datum['issuer_ticker'],
            stateincorp=datum['issuer_stateincorp'],
            irsnum=datum['issuer_irsnum'],
            classification=datum['issuer_classification'],
            fiscal_yearend=datum['issuer_fiscaleoy'],
            street1=datum['issuer_street1'],
            street2=datum['issuer_street2'],
            city=datum['issuer_city'],
            state=datum['issuer_state'],
            zipcode=datum['issuer_zip'],
        )

        issuer, _ = Company.objects.update_or_create(
            cik=issuer_cik,
            defaults=issuer_kwargs
        )

        kwargs = dict(
            owner=owner,
            issuer=issuer,
            accession_num=datum['accession_num'],
            datetime=datum['updated'],
            security=datum['transaction_security'],
            owner_istenpercentowner=datum['owner_istenpercentowner'],
            owner_sharesownedfollowingtransaction=\
                datum['transaction_sharesownedfollowingtransaction'],
            code=datum['transaction_code'],
            formtype=datum['form_type'],
            isequityswap=datum['isequityswap'],
            shares=datum['transaction_shares'],
            ownershipnature=datum['transaction_ownershiptype'],
            pricepershare=datum['transaction_pricepershare'],
            acqdisp_code=datum['transaction_acqdisp_code'],
        )

        logger.info(kwargs)

        # The new transaction to create.
        nonderivative = NonDerivative(**kwargs)
        nonderivative.save()

        message.append(f"{owner_cik}:{issuer_cik}")

    return HttpResponse(f"{request.method} {','.join(message)}", status=200)
