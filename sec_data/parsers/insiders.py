"""Parses XML files."""

from parsers.utils import getval
from parsers.utils import getnval
from parsers.utils import to_binary

from parsers.base import IssuerOwnerXMLParser

# Non-derivatives transactions that are labeled under the referened tags.
NDXML = (
    ('isequityswap', 'transactionCoding/equitySwapInvolved',),
    ('transaction_code', 'transactionCoding/transactionCode',),
)

# Non-derivatives transactions that are nested in the value tag of the
# referenced tag.
NDNXML = (
    ('transaction_security', 'securityTitle',),
    ('transaction_date', 'transactionDate',),
    ('transaction_shares', 'transactionAmounts/transactionShares',),
    (
        'transaction_pricepershare',
        'transactionAmounts/transactionPricePerShare',
    ),
    (
        'transaction_acqdisp_code',
        'transactionAmounts/transactionAcquiredDisposedCode',
    ),
    (
        'transaction_sharesownedfollowingtransaction',
        'postTransactionAmounts/sharesOwnedFollowingTransaction',
    ),
    ('transaction_ownershiptype', 'ownershipNature/directOrIndirectOwnership',),
)

NDBINARY = ('isequityswap',)

# Nonderivatives string floats that need to converted to a number.
NDUNSANITARY = (
    'transaction_shares', 'transaction_sharesownedfollowingtransaction',
)


# Derivatives transactions that are labeled under the referened tags.
DXML = (
    ('transaction_code', 'transactionCoding/transactionCode',),
    ('exercise_date', 'exerciseDate'),
)

# Derivatives transactions that are nested in the value tag of the referenced tag.
DNXML = (
    ('transaction_security', 'securityTitle',),
    ('transaction_convorexer_price', 'conversionOrExercisePrice',),
    ('transaction_date', 'transactionDate',),
    ('transaction_shares', 'transactionAmounts/transactionShares'),
    (
        'transaction_pricepershare',
        'transactionAmounts/transactionPricePerShare',
    ),
    (
        'transaction_acqdisp_code',
        'transactionAmounts/transactionAcquiredDisposedCode',
    ),
    ('expiration_date', 'expirationDate',),
    (
        'underlying_security_title',
        'underlyingSecurity/underlyingSecurityTitle',
    ),
    (
        'underlying_security_shares',
        'underlyingSecurity/underlyingSecurityShares',
    ),
    (
        'transaction_sharesownedfollowingtransaction',
        'postTransactionAmounts/sharesOwnedFollowingTransaction',
    ),
    ('transaction_ownershiptype', 'ownershipNature/directOrIndirectOwnership',),
)

DBINARY = ()

# Derivatives string floats that need to converted to a number.
DUNSANITARY = (
    'transaction_shares',
    'transaction_sharesownedfollowingtransaction',
    'underlying_security_shares',
)

NDTABLE_NODE = 'nonDerivativeTable'
NDTRANSACT_NODE = 'nonDerivativeTransaction'

DTABLE_NODE = 'derivativeTable'
DTRANSACT_NODE = 'derivativeTransaction'
DHOLDING_NODE = 'derivativeHolding'


class InsiderXMLParser(IssuerOwnerXMLParser):
    """
    xml: filebuffer in xml format.
    """

    def __init__(self, xml):

        super(InsiderXMLParser, self).__init__(xml)

        table_node = self.get_node(NDTABLE_NODE)
        args = [
            table_node, NDTRANSACT_NODE, NDXML, NDNXML, NDBINARY, NDUNSANITARY
        ]
        self.nds_transacts = self.get_transacts(*args) if table_node else []

        table_node = self.get_node(DTABLE_NODE)
        args = [
            table_node, DTRANSACT_NODE, DXML, DNXML, DBINARY, DUNSANITARY
        ]
        self.derivs_transacts = self.get_transacts(*args) if table_node else []

        args = [
            table_node, DHOLDING_NODE, DXML, DNXML, DBINARY, DUNSANITARY
        ]
        self.derivs_transacts.extend(
            self.get_transacts(*args) if table_node else []
        )


    def get_transacts(self, *args):
        """Get the individual transactions from the report"""

        table_node, transact_node, tags, nesttags, tobin, unsanitary = args

        transactions = []
        nodes = table_node.findall(transact_node) #pylint: disable=E1101
        doc = self.etree
        sanitize = lambda x: None if x is None else str(int(float(x)))

        for node in nodes:
            line = {}

            line.update({key: getval(node, tag, doc) for key, tag in tags})
            line.update({key: getnval(node, tag, doc) for key, tag in nesttags})

            line.update({key: to_binary(line[key]) for key in tobin})
            line.update({key: sanitize(line[key]) for key in unsanitary})

            transactions.append(line)

        return transactions
