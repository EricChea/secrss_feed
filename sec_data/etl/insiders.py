"""
Snippet of code to retreive data from the SEC Edgar RSS feed.
"""

import io
from datetime import datetime
import json
import urllib

from bs4 import BeautifulSoup
import requests

from settings import LOGGER
from settings import MYSQL_ND_API
from settings import NEW_FEED_URL
from settings import SEC_BASE_URL
from parsers.insiders import InsiderXMLParser


FORM_PARSER = {
    '3': InsiderXMLParser,
    '4': InsiderXMLParser,
    '5': InsiderXMLParser,
}


class ETL(object):
    """Extract Transform Load object for SEC files.

    This object is triggered by a feed to load an entry to our database.

    Args:
        entry (dict): a key/value store that desribes the typical features of an
            RSS feed. Derived from parsing an RSS feed.

    """

    def __init__(self, entry):

        self.entry = entry

        # Houses the flat text file representation of the data.
        self.text_data = None


    def __extract(self):
        """Retrieve raw filing data from each of the RSS feed entries"""

        # Navigate to the page containing links the data in different formats.
        LOGGER.info(f"Navigating to: {self.entry['datalink']}")
        htmldat = urllib.request.urlopen(self.entry['datalink'])
        page = BeautifulSoup(htmldat, 'lxml')

        # Used to locate the 'a' html that contains a link to downlad the filing
        # for the accession number in question
        search_word = self.entry['accession_num'] + '.' + 'txt'
        textpath = page.find('a', string=search_word, href=True)['href']
        url = SEC_BASE_URL + textpath

        LOGGER.info(f"Navigating to: {url}")
        self.text_data = urllib.request.urlopen(url)


    def __transform(self):
        """Transforms the data into a more malleable form"""

        # Skip past header parts of the filing
        xml = self.get_xml()

        # Select parser
        xmlparser = FORM_PARSER[self.entry['form_type']](xml)

        self.entry['issuer'].update(xmlparser.issuer_dscr)
        self.entry['owner'].update(xmlparser.owner_dscr)
        self.entry['nonderivatives'] = xmlparser.nds_transacts
        #self.entry['derivatives'] = xmlparser.derivs_transacts

        return


    def __load(self):
        """Load data into data stores"""
        jsondata = []
        base_data = self.__create_base_data()

        # Helper functions to convert datetimes into isoformat
        isdt = lambda x: 1 if isinstance(x, datetime) else 0
        toiso = lambda val: val.isoformat() if isdt(val) else val

        for transaction in self.entry['nonderivatives']:
            data = base_data
            data.update({'transaction_type': 'nonderivative'})
            data.update(transaction)

            jsondata.append({key:toiso(val) for key, val in data.items()})

        for transaction in self.entry['derivatives']:
            data = base_data
            data.update({'transaction_type': 'derivative'})
            data.update(transaction)

            jsondata.append({key:toiso(val) for key, val in data.items()})

        # Load data into SQL
        requests.post(MYSQL_ND_API, data=json.dumps(jsondata))

        # Trigger a refresh of the frontend
        requests.post(NEW_FEED_URL, data=json.dumps(['New Message']))


    def __create_base_data(self):
        """Transforms owner and issuer data to flattened descriptors"""
        base_keys = ('created', 'updated', 'accession_num', 'form_type')
        base_data = {key: self.entry[key] for key in base_keys}

        # Flatten nested dictionary and prefix with parent key.
        issuer = self.entry['issuer'].items()
        owner = self.entry['owner'].items()
        base_data.update({'issuer' + '_' + key: val for key, val in issuer})
        base_data.update({'owner' + '_' + key: val for key, val in owner})

        return base_data


    def get_xml(self):
        """Retrieve contents between (inclusive) <XML> AND </XML>"""
        while True:
            info = self.text_data.readline()\
                .decode('utf-8').replace('\t', '').strip()

            if info.split(':')[0] == '<XML>':
                break

        # Read XML and convert to filebuffer so it can be parsed by ElementTree
        info = self.text_data.read().decode('utf-8').replace('\t', '').strip()

        return io.StringIO(info[:info.find('</XML>')].replace('\n', ''))


    def run(self):
        """Executes the entire ETL process"""
        self.__extract()
        self.__transform()
        self.__load()
