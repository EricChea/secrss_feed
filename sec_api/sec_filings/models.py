"""Models for SEC filings"""

from django.db import models
from django.db import migrations

from django.db.models import CharField
from django.db.models import AutoField
from django.db.models import IntegerField
from django.db.models import DateTimeField
from django.db.models import PositiveSmallIntegerField
from django.db.models import DecimalField
from django.db.models import TextField

from django.db.models import ForeignKey


class CommonInfo(models.Model):
    name = CharField(max_length=1000, null=True)
    street1 = CharField(max_length=1000, null=True)
    street2 = CharField(max_length=1000, null=True)
    city = CharField(max_length=200, null=True)
    state = CharField(max_length=2, null=True)
    zipcode = CharField(max_length=10, null=True)

    class Meta:
        abstract = True


class Entity(CommonInfo):
    cik = CharField(max_length=10, unique=True, primary_key=True)

    class Meta:
        abstract = True


class Company(Entity):
    stateincorp = CharField(max_length=2, null=True)
    irsnum = IntegerField(null=True)
    classification = CharField(max_length=200, null=True)
    fiscal_yearend = IntegerField(null=True)
    ticker = CharField(max_length=5, null=True)


class Owner(Entity):
    isdirector = PositiveSmallIntegerField()
    isofficer = PositiveSmallIntegerField()
    officertitle = CharField(max_length=200, null=True)


class Transaction(models.Model):
    id = AutoField(primary_key=True)

    accession_num = CharField(max_length=20)

    # The datetime of the transaction
    datetime = DateTimeField(null=False)

    # The recipient in the transaction.
    owner = ForeignKey(Owner, on_delete=models.CASCADE)

    # The issuer of shares in the transaction -- typically a company giving ownership of itself.
    issuer = ForeignKey(Company, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class NonDerivative(Transaction):
    security = CharField(max_length=100)
    owner_istenpercentowner = PositiveSmallIntegerField()
    owner_sharesownedfollowingtransaction = IntegerField()

    code = CharField(max_length=1)
    formtype = PositiveSmallIntegerField()
    isequityswap = PositiveSmallIntegerField()
    shares = IntegerField()

    # D = Direct purchase, I = Indirect purchase.
    ownershipnature = CharField(max_length=1)

    # TODO: Create logic to extract price per share from text.
    # pricepershare = DecimalField(max_digits=10, decimal_places=2)
    pricepershare = TextField()

    # A = Owner acquires new shares, D = Owner disposes of shares.
    acqdisp_code = CharField(max_length=1)
