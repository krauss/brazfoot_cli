import time
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
        print(f'Finished in {end-start:.3} secs')
    return wrapper