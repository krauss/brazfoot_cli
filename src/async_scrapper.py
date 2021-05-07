import json
import asyncio
import aiohttp
import time
from game import GameCampeonatoBrasileiro, GameCopaDoBrasil
from utils import HEADERS
from bs4 import BeautifulSoup

#---------------------------------- Async Web Scrapping functions
async def async_scrapper(gameq, competition, division, season, is_all_games):
    start = time.time()

    async with aiohttp.ClientSession() as session:
        if competition == 'campeonato-brasileiro':
            await asyncio.gather(*(worker_1(gameq, f'https://www.cbf.com.br/futebol-brasileiro/competicoes/campeonato-brasileiro-serie-{division}/{season}/{game}', session, game) for game in range(1, 381)))

        else:
            await asyncio.gather(*(worker_2(gameq, f'https://www.cbf.com.br/futebol-brasileiro/competicoes/copa-brasil-masculino/{season}/{game}', session, game) for game in range(1, 173)))        

    elapsed = time.time()
    print(f'Finished in {elapsed-start:0.2f} seconds')

async def worker_1(gameq, url, session, game):
    #print(f'Downloading game {game}')
    response = await session.get(url=url, headers=HEADERS)
    if response.status == 200:
        val = await response.text()
        game_soup = BeautifulSoup(val, features="lxml")
        gameq.append(GameCampeonatoBrasileiro(game_soup, 'str'))

async def worker_2(gameq, url, session, game):
    #print(f'Downloading game {game}')
    response = await session.get(url=url, headers=HEADERS)
    if response.status == 200:
        val = await response.text()
        game_soup = BeautifulSoup(val, features="lxml")
        gameq.append(GameCopaDoBrasil(game_soup, 'str'))