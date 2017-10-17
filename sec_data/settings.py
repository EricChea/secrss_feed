"""Settings file for pulling data from the RSS feed."""

import logging as log
import os


# Establish connection to the Django server that houses all the APIs.
LOCAL_URL = 'http://127.0.0.1:8000'
PROD_URL = os.getenv('PROD_URL')
API_BASE_URL = LOCAL_URL if os.getenv('LOCAL') else PROD_URL

MYSQL_ND_API = ''.join([API_BASE_URL, '/sec/nonderivative/'])
NEW_FEED_URL = ''.join([API_BASE_URL, '/sec/nonderivative/newfeed/'])
ACCESSION_NUMS_ENDPOINT = ''.join([API_BASE_URL, '/sec/accessionnums/'])

# The Edgar URL is where the most recent files are polled from.
SEC_BASE_URL = 'https://www.sec.gov'
EDGAR_URL = ''.join([SEC_BASE_URL, '/cgi-bin/browse-edgar'])

# Forms that parsers have been built for.
SUPPORTED_FORMS = ('3', '4', '5')

ADDRESS_DSCR = (
    'name',
    'street1',
    'street2',
    'city',
    'state',
    'zip',
)

ISSUER_DSCR = (
    'classification',
    'cik',
    'irsnum',
    'stateincorp',
    'fiscaleoy',
    'ticker',
)

OWNER_DSCR = (
    'cik',
    'statedsc',
    'isdirector',
    'isofficer',
    'istenpercentowner',
    'officertitle',
)

LOGGER = log.getLogger()
HANDLER = log.StreamHandler()
FORMATTER = log.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
HANDLER.setFormatter(FORMATTER)
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(log.DEBUG)
