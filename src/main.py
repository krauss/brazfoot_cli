import time
import click
import os
import sys
import csv
import zipfile
from questionary import questionary, Choice
import xml.etree.ElementTree as ET
#from pymongo import MongoClient, InsertOne
sys.path.append(os.path.join(os.getcwd(), 'src'))
from game import BFGame
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests_futures.sessions import FuturesSession

#---------------------------------- Web Scrapping function
def scrapper(gameq, competition, division, season, is_all_games, file_format):    
    start_time = time.time()

    print(f'Fetching game data for competition {competition}...')
    with FuturesSession(executor=ThreadPoolExecutor(max_workers=10)) as session:
        futures = [session.get(f'https://www.cbf.com.br/futebol-brasileiro/competicoes/campeonato-brasileiro-serie-{division}/{season}/{game}') for game in range(1, 381 if is_all_games else 11)]

        for req in as_completed(futures):
            game_soup = BeautifulSoup(bytes(req.result().content), features="lxml")
            bfgame = BFGame(game_soup, 'str')
            gameq.append(bfgame)

    stop_time = time.time()
    print(f'Finished in {stop_time-start_time}')

#---------------------------------- Game processing function
def dumper(gameq, competition, division, season, is_all_games, file_format):
    start_time = time.time()
    #client = MongoClient(host='localhost', port=27017)

    #for game in sorted(game_queue, key=lambda x: x.competition_header['game_number']):
    #if client.football.brasileiro_serie_B.insert_one(game.get_game_dict()):
            #print(f"Game {game.competition_header['game_number']} saved successfully!")

    if file_format == 'json':        
        for game in gameq:
            try:
                with open(os.path.join(os.getcwd(), 'games', f'{game}.json'), 'w', encoding='utf-8') as json_file:
                    json_file.write(game.get_game_json())
            except OSError as err:
                print(f'Error: permission error {os.strerror(err.errno)}, stack_trace: {err.with_traceback()}')

            print(f"File ./games/{game}.json saved!")
    
    elif file_format == 'xml':
        for game in gameq:
            try:
                game.get_game_xml().write(os.path.join(os.getcwd(), 'games', f'{game}.xml'), encoding='utf-8', method='xml', xml_declaration=True)
            except OSError as err:
                print(f'Error: permission error {os.strerror(err.errno)}, stack_trace: {err.with_traceback()}')
                
            print(f"File ./games/{game}.xml saved!")
    
    else:            
        with open(os.path.join(os.getcwd(), 'games', f'{competition}-{division}-{season}.csv'), 'w', encoding='utf-8', newline='') as csv_file:
            try:
                writer = csv.writer(csv_file, delimiter=';')                
                for index, game in enumerate(gameq):
                    if index == 0:
                        writer.writerow(game.get_game_csv()[0])
                    writer.writerow(game.get_game_csv()[1])
            except PermissionError as err:
                print(f'Error: permission error {os.strerror(err.errno)}, stack_trace: {err.with_traceback()}')
        
        print(f"File ./games/{competition}-{division}-{season}.csv saved!")

    stop_time = time.time()
    print(f'Finished in {stop_time-start_time}')

#---------------------------------- 
bfgame_queue = []

#---------------------------------- Options available
lst_competition = [Choice('Campeonato Brasileiro', value='campeonato-brasileiro', checked=True), 
                    Choice('Copa do Brasil', value='copa-do-brasil', disabled=True)]

lst_divison = [Choice('Serie A', value='a'), Choice('Serie B', value='b')]
lst_season = [str(year) for year in range(2012, 2021)]
lst_file_format = [Choice('json'), Choice('xml'), Choice('csv')]

#---------------------------------- Main method
@click.command()
@click.option('-d', '--division', type=click.Choice(['a', 'b'], case_sensitive=False), help="The competition's division (A or B)")
@click.option('-s', '--season', type=click.IntRange(2012, 2020, clamp=True), help='What season, starting from 2012...2020')
@click.option('-f', '--file-format', type=click.Choice(['json', 'xml', 'csv'], case_sensitive=False), help='What format the game match files will be saved in (xml, json or csv)')
@click.option('--sample', is_flag=True, help="Extracts only the first 10 game matches")
def main(division=None, season=None, file_format=None, sample=False):
    """Brazillian Football Web Scrapper - CLI"""
    print("+", "-" * 40, "+")
    print("|", " " * 40, "|")
    print("|", "Brazillian Football Web Scrapper - CLI".center(40), "|")
    print("|", " " * 40, "|")
    print("+", "-" * 40, "+\n")
    
    if not all((division, season, file_format)):
        answer = questionary.form(
            competition = questionary.select("Select a competition", choices=lst_competition),
            division = questionary.select("Select a division", choices=lst_divison),
            season = questionary.select("Select a season", choices=lst_season),
            is_all_games = questionary.confirm("Do you want to extract all the games"),
            file_format = questionary.select("Select a file format", choices=lst_file_format)
        ).ask()

        scrapper(bfgame_queue, **answer)
        dumper(bfgame_queue, **answer)
    
    else:
        scrapper(bfgame_queue, 'campeonato-brasileiro', str(division).lower(), season, sample, file_format)
        dumper(bfgame_queue, 'campeonato-brasileiro', str(division).lower(), season, sample, file_format)

#---------------------------------- Entry point
if __name__ == '__main__':
    main()