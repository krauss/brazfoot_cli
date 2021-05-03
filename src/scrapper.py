from game import GameCampeonatoBrasileiro, GameCopaDoBrasil
from utils import timestamp_decorator
from bs4 import BeautifulSoup
from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession


#---------------------------------- Web Scrapping function
@timestamp_decorator
def scrapper(gameq, competition, division, season, is_all_games, file_format):    

    print(f'\nFetching game data for competition: {competition} {season}')

    if competition == 'campeonato-brasileiro':
        
        qty = 381 if is_all_games else 6 # How many games will be fetched
        wrks = 10 if is_all_games else 5 # number of threads 

        with FuturesSession(max_workers=wrks) as session:
            futures = [session.get(f'https://www.cbf.com.br/futebol-brasileiro/competicoes/campeonato-brasileiro-serie-{division}/{season}/{game}') for game in range(1, qty)]

            for req in as_completed(futures):
                if req.result().status_code == 200:
                    game_soup = BeautifulSoup(bytes(req.result().content), features="lxml")
                    bfgame = GameCampeonatoBrasileiro(game_soup, 'str')
                    gameq.append(bfgame)

    else:

        qty = 173 if is_all_games else 6 # How many games will be fetched
        wrks = 10 if is_all_games else 5 # number of threads
        
        with FuturesSession(max_workers=wrks) as session:
            
            futures = [session.get(f'https://www.cbf.com.br/futebol-brasileiro/competicoes/copa-brasil-masculino/{season}/{game}') for game in range(1, qty)]

            for req in as_completed(futures):
                if req.result().status_code == 200:
                    game_soup = BeautifulSoup(bytes(req.result().content), features="lxml")
                    bfgame = GameCopaDoBrasil(game_soup, 'str')
                    gameq.append(bfgame)