Introduction
------------
Eldorado data serves as the repository for pulling data from different sources.

Feeds
-----
This portion of the code interfaces with the external dataset and communicates
with ETL when there is work to be done.  An example of new work, is if the feed
has identified some new data coming from an external RSS feed.  The feed would
then create work for the ETL process.

ETL
---
The ETL process is dependent on a parser to get it's work done.  Currently,
parsers are specific to the data source and will be updated to be 'smarter'.
The extractor will do additional work to pull the data from the source that was 
provided. The transfomer uses the parser to format the data, make adjustments,
and other cleaning activities before passing the data to the loader.  The loader
will persist the transformed data.

Parsers
-------
These are the tools used by the transformers from ETL to prepare data for
persistence.

Usage
-----
The entrance for the module starts with the Feeds.  For example, to check the 
SEC RSS feed has new data run:
``python -m feeds.sec``

this will start a process that'll ping the sec RSS latest feeds for new filings.
If the criteria for a new feed is registered, a job is created for the ETL
worker, which uses an XML parser to transform the data.
