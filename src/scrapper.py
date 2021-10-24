import logging
from src.game import GameCampeonatoBrasileiro, GameCopaDoBrasil
from src.utils import timestamp_decorator, HEADERS, get_copa_do_brasil_games, get_campeonato_brasileiro_games
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
                url = 'https://www.cbf.com.br/futebol-brasileiro/competicoes/campeonato-brasileiro-serie-{0}/{1}/{2}'
                futures = [session.get(url.format(division, season, game), headers=HEADERS) for game in game_lst]
            
            except ConnectionError:
                logging.exception('Connection error!')
            except TimeoutError:
                logging.exception('Timeout error!')
            except Exception:
                logging.exception('Error!')

            else:
                for index, req in enumerate(as_completed(futures)):
                    print(f' Status: {(index / len(game_lst)):.1%}', end='\r')
                    if req.result().status_code == 200:
                        try:
                            game_soup = BeautifulSoup(bytes(req.result().content), features="html.parser")
                            bfgame = GameCampeonatoBrasileiro(game_soup, 'str')
                            gameq.append(bfgame)
                        except:
                            logging.exception(f"Error. Game: {bfgame.competition_header.get('game')}")
                    else:
                        logging.exception('Erro! Page not found.')

    else:

        game_lst = get_copa_do_brasil_games(season, is_all_games) # How many games will be fetched
        wrks = 10 if is_all_games else 5 # number of threads
        
        with FuturesSession(max_workers=wrks) as session:
            try:
                url = 'https://www.cbf.com.br/futebol-brasileiro/competicoes/copa-brasil-masculino/{0}/{1}'
                futures = [session.get(url.format(season, game), headers=HEADERS) for game in game_lst]
            
            except ConnectionError:
                logging.exception('Connection error!')
            except TimeoutError:
                logging.exception('Timeout error!')
            except Exception:
                logging.exception('Error!')

            else:
                for index, req in enumerate(as_completed(futures)):
                    print(f' Status: {(index / len(game_lst)):.1%}', end='\r')
                    if req.result().status_code == 200:
                        try:
                            game_soup = BeautifulSoup(bytes(req.result().content), features="html.parser")
                            bfgame = GameCopaDoBrasil(game_soup, 'str')
                            gameq.append(bfgame)
                        except:
                            logging.exception(f"Error. Game: {bfgame.competition_header.get('game')}")
                    else:
                        logging.exception('Erro! Page not found.')