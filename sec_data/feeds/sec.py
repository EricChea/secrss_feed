"""Latest filings feed"""
import json
from datetime import datetime
import urllib
from time import sleep
from threading import Thread

import feedparser
import requests

from settings import LOGGER
from settings import ACCESSION_NUMS_ENDPOINT
from settings import ISSUER_DSCR, OWNER_DSCR, ADDRESS_DSCR
from settings import EDGAR_URL
from settings import SUPPORTED_FORMS

from etl.insiders import ETL


def create_entry(data):
    """Creates a key/value store of data for a SEC filing

    The data that comes from the RSS feed does not contain detailed information
    on the owner of the new issuance, and details about the issuer such as their
    stock ticker.  This function creates a filing entry first hierchy that are
    described by the filing attributes such as issuer, owner, and the details
    of each transaction.

    Args:
        data (feedparser.FeedParserDict): a key/value store that desribes the
            typical features of an RSS feed.  Derived from parsing an RSS feed.

    Returns:
        dict: a key/value store that describes the attributes of an SEC filing.

    """

    for tag in data.tags:
        form_type = tag.term if tag.label == 'form type' else None

    if form_type is None:
        LOGGER.info("No form type detected: {accession_num}.")

    return dict(
        created=datetime.now(),
        accession_num=data.summary.split('<b>AccNo:</b> ')[1][:20],
        updated=data.updated,
        datalink=data.links[0].href,
        issuer=dict().fromkeys(ISSUER_DSCR + ADDRESS_DSCR, None),
        owner=dict().fromkeys(OWNER_DSCR + ADDRESS_DSCR, None),
        nonderivatives=[],
        derivatives=[],
        form_type=form_type,
    )


def verify_feed_status(feed):
    """Checks that the url to the feed is live.

    Args:
        feed (str): url to the feed.

    Returns:
        None: Will stop the process if the assertion is not met.

    """
    assert feed.status == 200, f"({feed.status}): Please check the feed."


def get_accession_nums():
    """Get accession numbers that are already stored

    Each SEC filing is given a unique accession number that allows regulatory
    agencies a means to look-up past filings.  Since the accession numbers are
    unique to each filing the accession numbers, from our database, can be
    retrieved in order to avoid duplicate entries.

    Returns:
        list: a list of accession numbers that are catalogued in the database.

    """
    response = requests.get(ACCESSION_NUMS_ENDPOINT, data='Data Please')

    assert response.status_code == 200, ' '.join([
        f"Status code {response.status_code} received when looking up",
        f"accession numbers from {ACCESSION_NUMS_ENDPOINT}"
    ])

    return json.loads(response.content)


class Filing(object):
    """The feed object pings the SEC website for new data.
    """

    # Number of most recent filings to pull. 100 is the max.
    n_filings = 100

    def __init__(self, rss_url):

        # Used for easy reference during a refresh of the rss contents.
        self.rss_url = rss_url
        self.feed = feedparser.parse(url_file_stream_or_string=rss_url)
        verify_feed_status(self.feed)

        self.accession_bank = get_accession_nums()


    def __is_process(self, form_type, accession_num):

        # The rss feed gives at least two records per form 4 -- one for the
        # issuer and one that is reporting (receiver) the transaction.
        # The function removes duplicates by the accession number.
        # Store entry data in a dictionary for better malleability
        # We are not supporting other filing types except insiders for now
        # If the accession number is already stored there is no need to
        # run a job to load it again.
        if form_type not in SUPPORTED_FORMS or accession_num in self.accession_bank:
            return False
        else:
            return True


    def __run_etl_jobs(self):
        """One trick pony. Loads data into the designated data store.

        If the summary data (entry) is an SEC filing and has not been noted in
        our datastore then create an ETL job to handle the persistence.

        Note: Since the backend databases are only called at the beginning of
        the process if more than one process is spun up, neither process will
        be aware of which accession numbers have been newly recorded.  This will
        most certainly lead to duplication of data.

        """

        for entry in self.feed.entries:
            entry_map = create_entry(entry)
            form_type = entry_map['form_type']
            accession_num = entry_map['accession_num']

            if self.__is_process(form_type, accession_num):
                etl = ETL(entry_map)
                etl.run()
                self.accession_bank.append(accession_num)


    def refresh(self, attempts=10):
        """Refreshes the rss feed.

        Refreshes the contents received from the RSS feed and sets 'self.feed'
        to the new feed contents.

        Args:
            attempts (int): number of attempts to refresh contents before
                stopping stopping.

        """

        for _ in range(attempts):

            feed_update = feedparser.parse(self.rss_url)

            # feedparser creates a 'status' attribute if there is a response
            if 'status' in feed_update:
                if feed_update.status == 304:
                    continue
                elif feed_update.status == 200:
                    self.feed = feed_update
                    return
            else:
                LOGGER.error(f"feed_update: {feed_update.bozo_exception}")

        LOGGER.info(f"{attempts} unnsuccessful attempts at refreshing data.")


    def run(self):
        """ Starts pinging the feed for data
        """

        while True:
            self.refresh()
            self.__run_etl_jobs()


def main():
    """Convenience runner"""

    params = dict(
        action='getcurrent',
        CIK='',
        type='',
        company='',
        dateb='',
        owner='include',
        start='0',
        count='100',
        output='atom'
    )

    url_param_string = '?'.join([EDGAR_URL, urllib.parse.urlencode(params)])
    edgarfeedparser = Filing(url_param_string)

    # Run the process for a full day.  This forces the process that runs the
    # feed to restart every day (86,400 seconds).
    thread = Thread(target=edgarfeedparser.run)
    thread.daemon = True
    thread.start()

    sleep(86400)

if __name__ == '__main__':
    import sys
    sys.exit(main())
