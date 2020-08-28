"""
Django management command to download SDN csv for use as fallback if the trade.gov API is down.

Command is run by Jenkins job each hour. By default the job runs on a three
hour time window starting one hour in the past.

For each order in the time window the command verifies exactly one payment of
the expected value exists in the database.

[come back and see what you'll want in the comments]
"""
import logging
import os
import requests
import sys
from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Management command to verify ecommerce transactions and log if there is any imbalance.'

    def handle(self, *args, **options):
        threshold = 4 # need to confirm what size, ticket mentioned 4 MB

        # download the csv locally
        url = 'http://api.trade.gov/static/consolidated_screening_list/consolidated.csv'

        with requests.Session() as s:
            download = s.get(url)  # couldn't tell if download is a csv or some other kind of object

        csv = open('temp_snd_fallback.csv', 'wb')
        csv.write(download.content)
        csv.close()
        file_size_in_bytes = os.path.getsize('temp_snd_fallback.csv')
        file_size_in_MB = file_size_in_bytes/1000000 # recommended way of (1024 * 1024) gave the wrong answer, see what's up

        if (file_size_in_MB > threshold): 
            print("we can go ahead! Call import for temp_snd_fallback.csv")
            # figure out how to have it kick off the import for file
            # delete local copy temp_snd_fallback.csv
        else: 
            raise CommandError("file download was too small!")
