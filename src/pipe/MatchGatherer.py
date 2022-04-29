from __future__ import annotations

import datetime
import re
import time

import requests
from bs4 import BeautifulSoup
import logging

SLEEP_BETWEEN_REQUESTS = 0.5
EMERGENCY_SLEEP = 60


class MatchGatherer:
    """
    The main class to gather match information for a given eventid
    """

    def __init__(self, event_id) -> None:
        self.__event_id = event_id
        self.matches = list()

    @property
    def event_id(self):
        return self.__event_id

    def get_matches_for_event(self) -> list[dict]:
        """
        Gather matches by a given eventid by looking for match urls in the main event page on hltv.org.
        Then using bs4 to scrape important match information
        :return: A list of dictionaries containg the match data as well as the download url for the demofile for a given
        match
        """
        offset = 0
        url = f'https://www.hltv.org/results?content=demo&event={self.event_id}'

        r = requests.get(url)
        html = r.content
        soup = BeautifulSoup(html, 'html.parser')
        matches = soup.find_all("div", {"class": "result-con"})
        match_urls = [
            f'https://www.hltv.org/{match.find("a").get("href")}' for match in matches]

        for url in match_urls:

            attempts = 0
            while attempts < 3:
                try:
                    r = requests.get(url)
                    assert r.status_code == 200
                    break
                except AssertionError as e:
                    attempts += 1
                    logging.warning(
                        f'⚠️ REQUEST GOT BLOCKED FOR MATCH URL: {url}|| RECEIVED STATUS: {r.status_code} --> 💤 SLEEP FOR {EMERGENCY_SLEEP} SEC')
                    time.sleep(EMERGENCY_SLEEP)
                    logging.warning('RETRYING NOW ...')

            html = r.content
            time.sleep(SLEEP_BETWEEN_REQUESTS)
            soup = BeautifulSoup(html, "html.parser")

            team_box = soup.find('div', {'class': 'standard-box teamsBox'})
            teams = team_box.find_all('div', {'class': 'team'})
            teams = [t.find('div', {'class': re.compile(
                r'(team-name|teamName)')}).get_text() for t in teams]
            teams = [t for t in teams if not t == '9z']

            date = soup.find('div', {'class': 'timeAndEvent'}).find(
                'div', {'class': 'time'}).get('data-unix')

            date = datetime.datetime.fromtimestamp(
                int(date) / 1000).strftime('%Y-%m-%d %H:%M:%S')

            urls = soup.find_all('a')

            hrefs = [url.get('href') for url in urls]
            for uri in hrefs:
                if isinstance(uri, str) and 'demo' in uri:
                    demo_url = uri
                    break

            demo_url = f'https://www.hltv.org{demo_url}'
            demo_id = demo_url.split('/')[5]

            match = {
                'entity': 'match',
                'teams': teams,
                'date_time': date,
                'match_url': url,
                'demo_id': demo_id,
                'demo_url': demo_url,
            }

            self.matches.append(match)


        return self.matches
