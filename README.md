# GoScrape 🐙:   Universal hltv.org demofile scraper
[![Build and publish Python 🐍 distributions 📦 to PyPI](https://github.com/mo-cmyk/goscrape/actions/workflows/publish-to-pypi.yml/badge.svg)](https://github.com/mo-cmyk/goscrape/actions/workflows/publish-to-pypi.yml)

Go scrape is a little open source project I created to make it easy to bulk download demofiles for the FPS CS:GO from the popular CS:GO fansite [hltv.org](hltv.org).


## Installation in Python - PyPi release

GoScrape is on [PyPi](https://pypi.org/project/goscrape/), so you can use `pip` to install it.

```bash
  pip install goscrape
```
    
## TL;DR

GoScrape consists of two main commands.

| command  | description                                                                                                                                                                                                           |
|----------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `events` | used in the first step to create a json lookup file containing important and structured information  about CS:GO esports events in a given timeframe and if specified also links to associated demofiles and matches. |
| `fetch`  | build on top of the events command and can be used to bulk download the demofile json output from the events command  otherwise a single event id can be specified to simply download demofiles for that event.       |

![tldr](https://raw.githubusercontent.com/mo-cmyk/goscrape/main/docs/images/tldr.svg)




## Getting Started

### Events 🎮
![events](https://raw.githubusercontent.com/mo-cmyk/goscrape/main/docs/images/events.svg)

| argument    | datatype | description                                                            | notes                                                                                     |                              |
|-------------|----------|------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|------------------------------|
| STARTDATE   | string   | the start date from when evet data should be gathered                  | formatted as string 'YYYY-MM-DD'                                                          | required                     |
| ENDDATE     | string   | the date to which event data should be gathered                        | formatted as string 'YYYY-MM-DD'                                                          | required                     |
| STORAGEPATH | string   | the directory or filepath to which the resulting json should be stored |                                                                                           | optional (default is cwd)    |
| MATCHES     | boolean  | whether match information and demofile urls should be scraped as well  | This flag is required if the resulting json file <br>should be used for the fetch command | optional (True if present)   |
| EVENT TYPE  | enum     | Which type of event datashould be pulled (Online, Lan ...)             |                                                                                           | optional (default is online) |


The Objects in the resulting json are identified by their event id given as a key and will look something like this: 

```json
{
  "6475": {
    "event_data": {
      "entity": "event",
      "event_id": "6475",
      "event_url": "https://www.hltv.org/events/6475/iem-dallas-2022-oceania-open-qualifier-2",
      "event_name_encoded": "iem-dallas-2022-oceania-open-qualifier-2",
      "event_name_full": "IEM Dallas 2022 Oceania Open Qualifier 2",
      "nr_of_teams": "8+",
      "prize": "Other",
      "event_type": "Online",
      "location": "Oceania (Online)",
      "event_start": "2022-04-20",
      "event_end": "2022-04-21"
    },
    "matches": [
      {
        "entity": "match",
        "teams": ["Paradox", "Aftershock"],
        "date_time": "2022-04-21 10:00:00",
        "match_url": "https://www.hltv.org//matches/2355881/paradox-vs-aftershock-iem-dallas-2022-oceania-open-qualifier-2",
        "demo_id": "71497",
        "demo_url": "https://www.hltv.org/download/demo/71497"
      }
    ]
  }
```


### Fetch 💾
![fetch](https://raw.githubusercontent.com/mo-cmyk/goscrape/main/docs/images/fetch.svg)

| argument        | datatype      | description                                                                                         | notes                                                                  |                              |
|-----------------|---------------|-----------------------------------------------------------------------------------------------------|------------------------------------------------------------------------|------------------------------|
| EVENT ID        | string \| int | the start date from when evet data should be gathered                                               | LOOKUP FILE & EVENT ID are mutually exclusive<br>only one can be used  | required                     |
| LOOKUP FILE     | string        | the filepath of the by the events command generated lookup that should be sued for demo downloading | LOOKUP FILE & EVENT ID are mutually exclusive <br>only one can be used | required                     |
| STORAGEPATH     | string        | the directory to which the demofiles should be written                                              |                                                                        | optional (default is cwd)    |
| MULTIPROCESSING | boolean       | whether multiprocessing should be utilized to speed up downloading                                  |                                                                        | optional (True if present)   |





## Changelog

### Version 0.1.3 (2022.09.22)

- Fixed a bug where the package failed to gather the file name of the provided demo file while using the fetch command

### Version 0.1.2 (2022.05.30)

- Bug fixes and improvements

### Version 0.1.1 (2022.04.29)

- Bug Fixes on multiprocessed downloading

### Version 0.1.0 (2022.04.24)

- Initial release

## Contributing

Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

