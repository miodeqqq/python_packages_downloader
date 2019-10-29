#!/usr/bin/env python

import json

import requests
from dateutil.parser import parse
from lxml.html import fromstring
from user_agent import generate_user_agent


class PythonPackagesCollector:
    """
    Python all versions scraper.
    """

    RELEASE_AND_URL = '//span[@class="release-number"]/a'

    RELEASE_DATE = '//span[@class="release-date"]/text()'

    PYTHON_VERSIONS_URLS_XPATH = './/tr/td/a/@href'

    def __init__(self, base_url):
        self.base_url = base_url

        self.session = self.init_session()

        self.collected_urls_data = None

    def init_session(self):
        """
        Initialises session obj.
        """

        headers = {
            'User-Agent': generate_user_agent()
        }

        with requests.Session() as s:
            s.headers.update(**headers)

            return s

    def fetch_all_versions_data(self):
        """
        Makes a request to the main url, parses content and returns expected data.
        """

        response = self.session.get(url=self.base_url)

        if response.status_code == 200:
            etree_obj = fromstring(response.text)

            self.release_numbers_and_urls = [(x.text.strip(), x.get('href')) for x in
                                             etree_obj.xpath(self.RELEASE_AND_URL)]

            self.release_dates = [parse(x) for x in etree_obj.xpath(self.RELEASE_DATE) if
                                  'release date' not in x.lower()]

    def build_proper_urls(self):
        """
        Build proper urls to visit.
        """

        PRE_URL = 'https://www.python.org'

        self.data = [
            {
                'release_date': item[0],
                'release_version': item[1][0],
                'url': f'{PRE_URL}{item[1][1]}'
            } for item in zip(self.release_dates, self.release_numbers_and_urls)
        ]

    def visit_collected_urls(self):
        """
        Visits urls and extend dict with download url.
        """

        for item in self.data:
            item['download_url'] = []

            response = self.session.get(url=item.get('url'))

            if response.status_code == 200:
                etree_obj = fromstring(response.text)

                item['download_url'].extend([x for x in etree_obj.xpath(self.PYTHON_VERSIONS_URLS_XPATH)])

    def save_results_to_json(self):
        """
        Dumps final data to JSON.
        """

        with open('results.json', 'w') as f:
            json.dump(self.data, f, indent=4, sort_keys=True, default=str)

    def run(self):
        """
        Runs the entire pipeline.
        """

        self.fetch_all_versions_data()
        self.build_proper_urls()
        self.visit_collected_urls()
        self.save_results_to_json()


p = PythonPackagesCollector(base_url='https://www.python.org/downloads/')
p.run()
