import time
import click
import os
import csv
from questionary import questionary, Choice
import xml.etree.ElementTree as ET
#from pymongo import MongoClient, InsertOne
from bs4 import BeautifulSoup
from game import BFGame
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests_futures.sessions import FuturesSession

def scrapper(gameq, competition, division, season, file_format):    
    start_time = time.time()

    print(f'Fetching game data for competition {competition}...')
    with FuturesSession(executor=ThreadPoolExecutor(max_workers=10)) as session:
        futures = [session.get(f'https://www.cbf.com.br/futebol-brasileiro/competicoes/campeonato-brasileiro-serie-{division}/{season}/{game}') for game in range(1, 381)]

        for req in as_completed(futures):
            game_soup = BeautifulSoup(bytes(req.result().content), features="lxml")
            game = BFGame(game_soup, 'str')
            gameq.append(game)

    stop_time = time.time()
    print(f'Finished in {stop_time-start_time}')


def dumper(gameq, competition, division, season, file_format):
    start_time = time.time()
    #client = MongoClient(host='localhost', port=27017)

    #for game in sorted(game_queue, key=lambda x: x.competition_header['game_number']):
    #if client.football.brasileiro_serie_B.insert_one(game.get_game_dict()):
            #print(f"Game {game.competition_header['game_number']} saved successfully!")

    if file_format == 'json':
        for game in gameq:
            
            with open(os.path.join(os.getcwd(), 'games', f'{game}.json'), 'w', encoding='utf-8') as json_file:
                json_file.write(game.get_game_json())
            
            print(f"File ./games/{game}.json saved!")
    
    elif file_format == 'xml':
        for game in gameq:
        
            game.get_game_xml().write(os.path.join(os.getcwd(), 'games', f'{game}.xml'), encoding='utf-8', method='xml', xml_declaration=True)
            
            print(f"File ./games/{game}.xml saved!")
    
    else:            
        with open(os.path.join(os.getcwd(), 'games', f'{competition}-{division}-{season}.csv'), 'w', encoding='utf-8', newline='') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')                
            for index, game in enumerate(gameq):
                if index == 0:
                    writer.writerow(game.get_game_csv()[0])
                writer.writerow(game.get_game_csv()[1])
            
        
        print(f"File ./games/{competition}-{division}-{season}.csv saved!")

    stop_time = time.time()
    print(f'Finished in {stop_time-start_time}')


game_queue = []

#---------- Options available
lst_competition = [Choice('Campeonato Brasileiro', value='campeonato-brasileiro', checked=True), 
                    Choice('Copa do Brasil', value='copa-do-brasil', disabled=True)]

lst_divison = [Choice('Serie A', value='a'), Choice('Serie B', value='b')]

lst_season = [str(year) for year in range(2012, 2021)]

lst_file_format = [Choice('json'), Choice('xml'), Choice('csv')]

#---------- Main method
@click.command()
@click.option('-d', '--division', help="The competition's division (A, B, First, Second etc...)")
@click.option('-s', '--season', type=int, help='What season, starting from 2012')
@click.option('-f', '--file-format', help='What file format the match game files will be saved in (xml, json or csv)')
def main(division=None, season=None, file_format=None):
    """Brazilian Football Web Scrapper - CLI"""
    print("#", "-" * 40, "#")
    print("#", " " * 40, "#")
    print("#", "Brazilian Football Web Scrapper - CLI".center(40), "#")
    print("#", " " * 40, "#")
    print("#", "-" * 40, "#\n")
    
    if not all((division, season, file_format)):
        answer = questionary.form(
            competition = questionary.select("Select the competition", choices=lst_competition),
            division = questionary.select("Select the division", choices=lst_divison),
            season = questionary.select("Select the season", choices=lst_season),
            file_format = questionary.select("Select the file format", choices=lst_file_format)
        ).ask()

        scrapper(game_queue, **answer)
        dumper(game_queue, **answer)
    
    else:
        scrapper(game_queue, 'campeonato-brasileiro', division, season, file_format)
        dumper(game_queue, 'campeonato-brasileiro', division, season, file_format)

#---------- Entry point
if __name__ == '__main__':
    main()