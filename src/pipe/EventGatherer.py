import datetime
import json
import logging
import os
import time
import urllib.parse

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from src.pipe.EventType import EventType
from src.pipe.MatchGatherer import MatchGatherer

SLEEP_BETWEEN_REQUESTS = 0.1
EMERGENCY_SLEEP = 60


class EventGatherer:
    """
    Main class to gather information on events based on a given timeframe
    """

    def __init__(self) -> None:
        self.events = dict()

    @staticmethod
    def _request_page(start: str, end: str, type: EventType, offset: int = 0) -> requests.Response:
        if type is EventType.ALL:
            url = f'https://www.hltv.org/events/archive?startDate={urllib.parse.quote(start)}&endDate={urllib.parse.quote(end)}&offset={urllib.parse.quote(str(offset))}'
        else:
            url = f'https://www.hltv.org/events/archive?startDate={urllib.parse.quote(start)}&endDate={urllib.parse.quote(end)}&eventType={urllib.parse.quote(type.value)}&offset={urllib.parse.quote(str(offset))}'
        r = requests.get(url)
        return r

    def _extract_events(self, response: requests.Response) -> bool:
        html = response.content
        soup = BeautifulSoup(html, "html.parser")
        events = soup.find_all(
            "a", {"class": "a-reset small-event standard-box"})

        def __extract_event(event):
            href = event.get("href")
            url_components = href.split('/')
            entity = url_components[1]
            id = url_components[2]
            name_encoded = url_components[3]
            event_url = f'https://www.hltv.org{href}'

            trs = event.find_all('tr')
            overview = trs[0]
            tds = overview.find_all('td')

            event_name = tds[0].get_text().strip()
            teams = tds[1].get_text()
            prize = tds[2].get_text()
            event_type = tds[3].get_text()

            details = trs[1].find('td').find_all('span')

            location = details[0].find(
                'span').get_text().replace('|', '').strip()
            dates = details[2].find_all('span', {"data-time-format": "MMM do"})
            start = dates[0]
            if len(dates) == 1:
                end = start
            else:
                end = dates[1]

            start = datetime.datetime.fromtimestamp(
                int(start.get('data-unix')) / 1000).strftime('%Y-%m-%d')
            end = datetime.datetime.fromtimestamp(
                int(end.get('data-unix')) / 1000).strftime('%Y-%m-%d')

            return {"event_data": {
                'entity': 'event',
                'event_id': id,
                'event_url': event_url,
                'event_name_encoded': name_encoded,
                'event_name_full': event_name,
                'nr_of_teams': teams,
                'prize': prize,
                'event_type': event_type,
                'location': location,
                'event_start': start,
                'event_end': end,
            }}

        for _i, event in enumerate(tqdm(events, desc=f'Gathering events')):
            extracted_event = __extract_event(event=event)
            tqdm.write(
                f'Getting Data for event ID:{extracted_event["event_data"]["event_id"]} {extracted_event["event_data"]["event_name_full"]}')
            self.events[extracted_event['event_data']
                        ['event_id']] = extracted_event

        if len(events) < 50:
            return True
        else:
            return False

    def get_events_lookup(self, start: str = '2021-04-22', end: str = '2022-04-22', type: EventType = EventType.ONLINE,
                          get_matches: bool = True, storage_path: str = None) -> None:
        """
        Creates a lookup for events in a given timeframe to be able to later download the demofiles for given events if
        matches is specified
        :param start: The start date from which demofiles should eb downloaded given as a string in format 'YYYY-MM-DD'
        :param end: The end date to which demofiles should eb downloaded given as a string in format 'YYYY-MM-DD'
        :param type: The EventType of events that should be considered
        :param get_matches: Whether match data and demofile urls should also be considered and added to the lookup
        :param storage_path: The directory or fileopath to which the resulting ouput json file should be written
        :return: None
        """
        print(
            f'Now gathering CS:GO events from 🕰{start} to {end} 🏁 with type {type.name}.')
        if get_matches:
            print(f'Also getting matches as well 🕹')

        offset = 0
        while True:
            attempts = 0
            while attempts < 3:
                try:
                    r = self._request_page(start=start, end=end,
                                           type=type, offset=offset)
                    assert r.status_code == 200
                    break
                except AssertionError as e:
                    attempts += 1
                    logging.warning(
                        f'⚠️ REQUEST GOT BLOCKED ON OFFSSET: {offset} || RECEIVED STATUS: {r.status_code} --> 💤 SLEEP FOR {EMERGENCY_SLEEP} SEC')
                    time.sleep(EMERGENCY_SLEEP)
                    logging.warning('RETRYING NOW ...')

            done = self._extract_events(r)
            if not done:
                offset += 50
                time.sleep(SLEEP_BETWEEN_REQUESTS)
            else:
                break

        print(f'Found all events in given period ✅')

        if get_matches:
            print('Now looking for matches ... ⏳')
            for e in tqdm(self.events.items(), desc='Getting match data'):
                event = e[1]
                tqdm.write(
                    f"Getting  match 🎮 data for event {event['event_data']['event_name_full']} ")
                id = e[0]
                gatherer = MatchGatherer(event_id=id)
                matches = gatherer.get_matches_for_event()
                self.events[id]['matches'] = matches

        print(f'Found all matches in given period ✅')

        print(f'Saving lookup ... ⌛️')
        if storage_path is None:
            path = os.getcwd()
            file_location = os.path.join(
                path, f'event_lookup__{start.replace("-", "_")}__{end.replace("-", "_")}__{type.value}.json')

            with open(file_location, 'w') as fp:
                json.dump(self.events, fp)

            print('Lookup file saved ✅')
            print('==='*30)
            print(f"File can be found at: {file_location}")
        else:
            file_location = os.path.join(storage_path,
                                         f'event_lookup__{start.replace("-", "_")}__{end.replace("-", "_")}__{type.value}.json')
            with open(file_location, 'w') as fp:
                json.dump(self.events, fp)

            print('Lookup file saved ✅')
            print('==='*30)
            print(f"File can be found at: {file_location}")
