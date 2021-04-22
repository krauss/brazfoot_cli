import time
import click
import os
import csv
from questionary import questionary, Choice
from .game import GameCampeonatoBrasileiro, GameCopaDoBrasil
from bs4 import BeautifulSoup
from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession

#---------------------------------- Web Scrapping function
def scrapper(gameq, competition, division, season, is_all_games, file_format):    
    start_time = time.time()

    print(f'\nFetching game data for competition: {competition} {season}...')

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

    stop_time = time.time()
    print(f'Fetching finished in {stop_time-start_time:.3} sec')

#---------------------------------- Game processing function
def dumper(gameq, competition, division, season, is_all_games, file_format):
    start_time = time.time()

    if file_format == 'json':        
        for game in gameq:
            try:
                with open(os.path.join(os.getcwd(), 'export', f'{game}.json'), 'w', encoding='utf-8') as json_file:
                    json_file.write(game.get_game_json())
            except OSError as err:
                print(f'Error: permission error {os.strerror(err.errno)}, stack_trace: {err.with_traceback()}')

            print(f"File ./export/{game}.json saved!")
    
    elif file_format == 'xml':
        for game in gameq:
            try:
                game.get_game_xml().write(os.path.join(os.getcwd(), 'export', f'{game}.xml'), encoding='utf-8', method='xml', xml_declaration=True)
            except OSError as err:
                print(f'Error: permission error {os.strerror(err.errno)}, stack_trace: {err.with_traceback()}')
                
            print(f"File ./export/{game}.xml saved!")
    
    else:            
        with open(os.path.join(os.getcwd(), 'export', f'{competition}-{division}-{season}.csv'), 'w', encoding='utf-8', newline='') as csv_file:
            try:
                writer = csv.writer(csv_file, delimiter=';')                              
                for index, game in enumerate(gameq):
                    if index == 0:
                        writer.writerow(game.get_game_csv()[0])
                    writer.writerow(game.get_game_csv()[1])
            except PermissionError as err:
                print(f'Error: permission error {os.strerror(err.errno)}, stack_trace: {err.with_traceback()}')
        
        print(f"File ./export/{competition}-{division}-{season}.csv saved!")

    stop_time = time.time()
    print(f'Saving finished in {stop_time-start_time:.3} sec')

#---------------------------------- 
bfgame_queue = []

#---------------------------------- Options available
lst_competition = [Choice('Campeonato Brasileiro', value='campeonato-brasileiro'), 
                    Choice('Copa do Brasil', value='copa-do-brasil')]
lst_divison = [Choice('Serie A', value='a'), Choice('Serie B', value='b')]
lst_season = [str(year) for year in range(2012, 2021)]
lst_file_format = [Choice('json'), Choice('xml'), Choice('csv')]

#---------------------------------- Main method
@click.command()
@click.option('-c', '--competition', type=click.Choice(['campeonato-brasileiro', 'copa-do-brasil'], case_sensitive=False))
@click.option('-d', '--division', type=click.Choice(['a', 'b'], case_sensitive=False))
@click.option('-s', '--season', type=click.IntRange(2012, 2020, clamp=True), help='What season, starting from 2012...2020')
@click.option('-f', '--file-format', type=click.Choice(['json', 'xml', 'csv'], case_sensitive=False))
@click.option('--sample', is_flag=True, help="Extracts only the first 10 game matches")
def main(competition=None, division=None, season=None, file_format=None, sample=False):
    """Brazillian Football Web Scrapper - CLI"""
    print("+", "-" * 40, "+")
    print("|", " " * 40, "|")
    print("|", "Brazillian Football Web Scrapper - CLI".center(40), "|")
    print("|", " " * 40, "|")
    print("+", "-" * 40, "+\n")
    
    if not all((division, season, file_format)):
        competition = questionary.select("Select a competition", choices=lst_competition).ask()
        division = questionary.select("Select a division", choices=lst_divison).skip_if(competition == 'copa-do-brasil', default='a').ask()
        season = questionary.select("Select a season", choices=lst_season).ask()
        is_all_games = questionary.confirm("Download all the games?").ask()
        file_format = questionary.select("Select a file format", choices=lst_file_format).ask()

        scrapper(bfgame_queue, competition, division, season, is_all_games, file_format)
        dumper(bfgame_queue, competition, division, season, is_all_games, file_format)
    
    else:
        scrapper(bfgame_queue, competition, str(division).lower(), season, sample, file_format)
        dumper(bfgame_queue, competition, str(division).lower(), season, sample, file_format)

#---------------------------------- Entry point
if __name__ == '__main__':
    main()