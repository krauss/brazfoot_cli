import time
import click
import os
from questionary import questionary, Choice
import xml.etree.ElementTree as ET
from pymongo import MongoClient, InsertOne
from bs4 import BeautifulSoup
from game import BFGame
from threading import Event
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests_futures.sessions import FuturesSession

def producer(gameq, competition, division, season, file_format):    
    start_time = time.time()

    print(f'Fetching game data for competition {competition}...')
    with FuturesSession(executor=ThreadPoolExecutor(max_workers=10)) as session:
        futures = [session.get(f'https://www.cbf.com.br/futebol-brasileiro/competicoes/campeonato-brasileiro-serie-{division}/{season}/{game}') for game in range(1, 11)]

        for req in as_completed(futures):
            game_soup = BeautifulSoup(bytes(req.result().content), features="lxml")
            game = BFGame(game_soup, 'str')
            gameq.append(game)

    stop_time = time.time()
    print(f'Finished in {stop_time-start_time}')


def consumer(gameq, file_format):
    start_time = time.time()
    #client = MongoClient(host='localhost', port=27017)

    #for game in sorted(game_queue, key=lambda x: x.competition_header['game_number']):
    #if client.football.brasileiro_serie_B.insert_one(game.get_game_dict()):
            #print(f"Game {game.competition_header['game_number']} saved successfully!")

    if file_format == 'json':
        for game in game_queue:
            
            with open(os.path.join(os.getcwd(), 'games', f'game_{game.competition_header["game_number"]}.json'), 'w') as json_file:
                json_file.write(game.get_game_json())
            
            print(f"File ./games/game_{game.competition_header['game_number']}.json saved!")
    
    elif file_format == 'xml':
        for game in game_queue:
        
            game.get_game_xml().write(os.path.join(os.getcwd(), 'games', f'game_{game.competition_header["game_number"]}.xml'), encoding='utf-8', method='xml', xml_declaration=True)
            
            print(f"File ./games/game_{game.competition_header['game_number']}.xml saved!")

    stop_time = time.time()
    print(f'Finished in {stop_time-start_time}')



game_queue = []

#-------- Options available
competition = [Choice('Campeonato Brasileiro', checked=True), Choice('Copa do Brasil', disabled=True)]
divison = [Choice('Serie A', value='a', checked=True), Choice('Serie B', value='b')]
season = [str(year) for year in range(2012, 2021)]
file_format = [Choice('json', checked=True), Choice('xml'), Choice('csv', disabled=True)]

#---------- Main method
@click.command()
def main():
    """Brazilian Football Web Scrapper - CLI"""
    print("#", "-" * 40, "#")
    print("#", " " * 40, "#")
    print("#", "Brazilian Football Web Scrapper - CLI".center(40), "#")
    print("#", " " * 40, "#")
    print("#", "-" * 40, "#\n")
    
    answer = questionary.form(
        competition = questionary.select("Select the competition", choices=competition),
        division = questionary.select("Select the division", choices=divison),
        season = questionary.select("Select the season", choices=season),
        file_format = questionary.select("Select the file format", choices=file_format)
    ).ask()

    producer(game_queue, **answer)
    consumer(game_queue, answer['file_format'])

#---------- Entry point
if __name__ == '__main__':
    main()