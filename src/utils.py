import time
import platform
from datetime import datetime

#----------------- Helper functions --------------------------------------
def parse_datetime(date=None, time=None, mode='str'):
    month = {
        'Janeiro': '01',
        'Fevereiro': '02',
        'Março': '03',
        'Abril': '04',
        'Maio': '05',
        'Junho': '06',
        'Julho': '07',
        'Agosto': '08',
        'Setembro': '09',
        'Outubro': '10',
        'Novembro': '11',
        'Dezembro': '12'
    }
    date = '-'.join(reversed([ date.strip() if index != 1 else month[date.strip()] for index, date in enumerate(date.split(',')[1].split('de'))]))
    return datetime.fromisoformat(date + ' ' + time.strip()) if mode == 'date' else date + ' ' + time.strip()


def timestamp_decorator(func):
    """Decorator that stamps the time a function takes to execute."""
    def wrapper(*args, **kwargs):
        start = time.time()

        func(*args, **kwargs)        

        end = time.time()
        print(f' Finished in {end-start:.3} secs')
    return wrapper

LINUX = {
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Sec-GPC": "1",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9"
}

WINDOWS = {
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36 Edg/90.0.818.46",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
}

# Define different headers for different platforms
if platform.system() == 'Linux':
    HEADERS = LINUX

elif platform.system() == 'Windows':
    HEADERS = WINDOWS

# Function to mapping a season to its respective qty of games.
def get_copa_do_brasil_games(season, all_games):
    game_lst = {
        '2012': 126,
        '2013': 172,
        '2014': 172,
        '2015': 172,
        '2016': 170,
        '2017': 120,
        '2018': 120,
        '2019': 120,
        '2020': 120
    }
    return range(1, game_lst[season]+1) if all_games else range(1, 6)

# Function to mapping a season to its respective qty of games.
def get_campeonato_brasileiro_games(division, season, all_games):
    game_lst = {
        'a': {
            '2012': 380,
            '2013': 380,
            '2014': 380,
            '2015': 380,
            '2016': 380,
            '2017': 380,
            '2018': 380,
            '2019': 380,
            '2020': 380,
            '2021': 380
        },
        'b': {
            '2012': 380,
            '2013': 380,
            '2014': 380,
            '2015': 380,
            '2016': 380,
            '2017': 380,
            '2018': 380,
            '2019': 380,
            '2020': 380,
            '2021': 380
        },
        'c': {
            '2012': 195,
            '2013': 220,
            '2014': 194,
            '2015': 194,
            '2016': 194,
            '2017': 194,
            '2018': 194,
            '2019': 194,
            '2020': 206,
            '2021': 206
        },
        'd': {
            '2012': 190,
            '2013': 190,
            '2014': 200,
            '2015': 190,
            '2016': 266,
            '2017': 266,
            '2018': 266,
            '2019': 266,
            '2020': 518,
            '2021': 518       
        }
    }

    return range(1, game_lst[division][season]+1) if all_games else range(1, 6)