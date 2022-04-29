import itertools
import json
import logging
import multiprocessing as mp
import os
import time
from pathlib import Path

import requests
from src.pipe.MatchGatherer import MatchGatherer
from tqdm import tqdm

SLEEP_BETWEEN_REQUESTS = 0.5
EMERGENCY_SLEEP = 60


class DemoDownloader:
    """
    The main class to download demofiles
    """

    def __init__(self) -> None:
        pass

    def _download_file(self, match, event_id, output_file):
        demo_url = match['demo_url']
        demo_id = match['demo_id']
        path = os.path.join(output_file, 'demofiles', f'{event_id}')
        Path(path).mkdir(parents=True, exist_ok=True)
        tqdm.write(
            f'🌍 Downloading demofile for event: {event_id} from {demo_url} 👉 {path}')
        attempts = 0
        while attempts < 3:
            try:
                r = requests.get(demo_url, stream=True)
                assert r.status_code == 200
                file_location = os.path.join(path, demo_id)
                file_location = f'{file_location}.rar'
                total_size_in_bytes = int(r.headers.get('content-length', 0))
                block_size = 1024  # 1 Kibibyte
                progress_bar = tqdm(total=total_size_in_bytes,
                                    unit='iB', unit_scale=True, desc='Downloading')
                with open(file_location, 'w') as file:
                    for data in r.iter_content(block_size):
                        progress_bar.update(len(data))
                    file.write(data)
                    progress_bar.close()
                print(f'File saved to {file_location}')
                break
            except AssertionError as e:
                attempts += 1
                logging.warning(
                    f'⚠️ DOWNLOAD REQUEST GOT BLOCKED FOR DEMO URL: {demo_url}|| RECEIVED STATUS: {r.status_code} --> 💤 SLEEP FOR {EMERGENCY_SLEEP} SEC')
                time.sleep(EMERGENCY_SLEEP)
                logging.warning('RETRYING NOW ...')

        time.sleep(SLEEP_BETWEEN_REQUESTS)

    def _download_for_single_event(self, event_id: int, output_file: str, multiprocessing: bool) -> None:
        
        # Ensure at least 1 core 
        cpu_count = os.cpu_count()
        cpu_count = cpu_count - 1
        if cpu_count <= 1:
            multiprocessing = False
        
        match_finder = MatchGatherer(event_id=event_id)
        matches = match_finder.get_matches_for_event()
        print(f'Found {len(matches)} match(es) for event with id {event_id}')
        if multiprocessing:
            print(f'Utilizing {cpu_count} core(s) 📡')
            with mp.Pool(cpu_count) as pool:
                pool.starmap(self._download_file, zip(matches, itertools.repeat(event_id), itertools.repeat(output_file)))
                

        else:
            for match in matches:
                self._download_file(match, event_id=event_id,
                                    output_file=output_file)

        print(f"Download for event with id: {event_id} done ✅")

    def _download_for_multiple_events(self, event_file: str, output_file: str, multiprocessing: bool) -> None:
        
        # Ensure at least 1 core 
        cpu_count = os.cpu_count()
        cpu_count = cpu_count - 1
        if cpu_count <= 1:
            multiprocessing = False
        
        with open(event_file, 'r') as fp:
            event_data = json.load(fp)

        print(
            f'Found {len(event_data.items())} events in the provided lookup file! 📂')
        
        
        for e in event_data.items():
            event_id = e[0]
            event = e[1]

            matches = event.get('matches')
            
            if matches is None or len(matches) == 0:
                print(f'No matches found for event: {event.get("event_data").get("event_name_full")}!')
                continue
            
            print(f'Found {len(matches)} match for event: {event.get("event_data").get("event_name_full")}! 🏋️‍♀️')
            
            
            
            if multiprocessing:
                with mp.Pool(cpu_count) as pool:
                    pool.starmap(self._download_file, zip(matches, itertools.repeat(event_id), itertools.repeat(output_file)))
                print(f'Utilizing {cpu_count} core(s) 📡')
            else:
                for match in matches:
                  self._download_file(
                      match, event_id=event_id, output_file=output_file)

            print(
                f"Download for event: {event.get('event_data')['event_name_full']} with id: {event_id} done ✅")

    def download_demos(self, event_id=None, event_file: str = None, output_file: str = None,
                       multiprocessing: bool = False):
        """
        Function used to download demofiles either by providing a lookup file or a given eventid
        :param event_id:
        :param event_file:
        :param output_file:
        :param multiprocessing:
        :return:
        """

        if output_file is None:
            path = os.getcwd()
        if event_id is not None:
            print(
                f'Now downloading demofiles for single event with id {event_id} ... ⏳')
            event_id = int(event_id)
            if multiprocessing:
                print(f'Also utilizing multiprocessing 🧑‍💻') 
            self._download_for_single_event(
                event_id=event_id, output_file=path, multiprocessing=multiprocessing)
            
            
        elif event_file is not None:
            print(f'Now downloading demofiles for provided events lookup file ... ⏳')
            if multiprocessing:
                print(f'Also utilizing multiprocessing 🧑‍💻') 
            self._download_for_multiple_events(
                event_file=event_file, output_file=path, multiprocessing=multiprocessing)
        else:
            raise Exception(
                'EITHER AN EVENT ID OR LOOKUP FILE MUST BE PROVIDED!')

        print('Download done !✅')

        