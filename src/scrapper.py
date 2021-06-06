import logging
from .game import GameCampeonatoBrasileiro, GameCopaDoBrasil
from .utils import timestamp_decorator, HEADERS, get_copa_do_brasil_games, get_campeonato_brasileiro_games
from bs4 import BeautifulSoup
from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession

#---------------------------------- Web Scrapping function
@timestamp_decorator
def scrapper(gameq, competition, division, season, is_all_games):    

    print(f'\n Fetching data\n')

    if competition == 'campeonato-brasileiro':
        
        game_lst = get_campeonato_brasileiro_games(division, season, is_all_games) # How many games will be fetched
        wrks = 10 if is_all_games else 5 # number of threads 

        with FuturesSession(max_workers=wrks) as session:
            try:

                futures = [session.get(f'https://www.cbf.com.br/futebol-brasileiro/competicoes/campeonato-brasileiro-serie-{division}/{season}/{game}', headers=HEADERS) for game in game_lst]
            
            except ConnectionError as conerr:
                logging.critical('Connection error: %s', conerr)
            except TimeoutError as timerr:
                logging.critical('Timeout error: %s', timerr)
            except Exception as ex:
                logging.critical('Error: %s', ex)

            else:
                for index, req in enumerate(as_completed(futures)):
                    print(f' Status: {(index / len(game_lst)):.1%}', end='\r')
                    if req.result().status_code == 200:
                        game_soup = BeautifulSoup(bytes(req.result().content), features="lxml")
                        bfgame = GameCampeonatoBrasileiro(game_soup, 'str')
                        gameq.append(bfgame)

    else:

        game_lst = get_copa_do_brasil_games(season, is_all_games) # How many games will be fetched
        wrks = 10 if is_all_games else 5 # number of threads
        
        with FuturesSession(max_workers=wrks) as session:
            try:

                futures = [session.get(f'https://www.cbf.com.br/futebol-brasileiro/competicoes/copa-brasil-masculino/{season}/{game}', headers=HEADERS) for game in game_lst]
            
            except ConnectionError as conerr:
                logging.critical('Connection error: %s', conerr)
            except TimeoutError as timerr:
                logging.critical('Timeout error: %s', timerr)
            except Exception as ex:
                logging.critical('Error: %s', ex)

            else:
                for index, req in enumerate(as_completed(futures)):
                    print(f' Status: {(index / len(game_lst)):.1%}', end='\r')
                    if req.result().status_code == 200:
                        game_soup = BeautifulSoup(bytes(req.result().content), features="lxml")
                        bfgame = GameCopaDoBrasil(game_soup, 'str')
                        gameq.append(bfgame)