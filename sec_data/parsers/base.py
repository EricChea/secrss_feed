"""Parses SEC forms for issuer portion of data."""

import xml.etree.ElementTree as ET

from parsers.utils import getval
from parsers.utils import to_binary


ISSUER_NODE = 'issuer'
OWNER_NODE = 'reportingOwner'

ISSUERXML = (
    ('cik', 'issuerCik',),
    ('name', 'issuerName',),
    ('ticker', 'issuerTradingSymbol',),
)
# Owner datums that are labeled under the referened tags.
OWNERXML = (
    ('cik', 'reportingOwnerId/rptOwnerCik',),
    ('name', 'reportingOwnerId/rptOwnerName',),
    ('street1', 'reportingOwnerAddress/rptOwnerStreet1',),
    ('street2', 'reportingOwnerAddress/rptOwnerStreet2',),
    ('city', 'reportingOwnerAddress/rptOwnerCity',),
    ('state', 'reportingOwnerAddress/rptOwnerState',),
    ('zip', 'reportingOwnerAddress/rptOwnerZipCode',),
    ('statedsc', 'reportingOwnerAddress/rptOwnerStateDescription',),
    ('officertitle', 'reportingOwnerRelationship/officerTitle',),
    ('isdirector', 'reportingOwnerRelationship/isDirector',),
    ('isofficer', 'reportingOwnerRelationship/isOfficer',),
    ('istenpercentowner', 'reportingOwnerRelationship/isTenPercentOwner',),
)
OWNER_BINARY = ('isdirector', 'isofficer', 'istenpercentowner',)


class IssuerOwnerXMLParser(object):
    """
    xml: filebuffer in xml format.
    """

    def __init__(self, xml):
        self.etree = ET.parse(xml)

        self.issuer_dscr = self.get_issuer_description()
        self.owner_dscr = self.get_owner_description()


    def get_issuer_description(self):
        """Retrieve data from issuer child nodes"""
        doc = self.etree
        node = self.etree.find(ISSUER_NODE)
        return {key: getval(node, tag, doc) for key, tag in ISSUERXML}


    def get_owner_description(self):
        """Retrieve data from owner child nodes"""
        doc = self.etree
        node = self.etree.find(OWNER_NODE)
        owner = {}

        owner.update({key: getval(node, tag, doc) for key, tag in OWNERXML})

        # Convert boolean (string fields) to binary 0 for no, 1 for yes
        owner.update({key: to_binary(owner[key]) for key in OWNER_BINARY})

        return owner


    def get_node(self, node):
        """Get non derivatives table from report"""
        return self.etree.find(node)
