import click
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from questionary import questionary, Choice
from src.scrapper import scrapper
from src.exporter import exporter

#---------------------------------- Logger settings
def set_logger():
    # Define configuracoes basicas para o logger
    msg_frt = "[%(asctime)s.%(msecs)03d] %(levelname)s [%(name)s] - %(message)s"
    time_frt = "%Y-%m-%d %H:%M:%S"
    # Define o nome do arquivo de log baseado na env BOT_NAME
    log_path = Path.joinpath(Path.cwd(), 'log', 'brazfoot_cli.log').as_posix()
    formatter = logging.Formatter(msg_frt, time_frt)
    handler = RotatingFileHandler(log_path, backupCount=0, maxBytes=102400)
    
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel('INFO')
    logging.getLogger().name = 'brazfoot_cli'

#---------------------------------- 
bfgame_queue = []

#---------------------------------- Options available
lst_competition = [
    Choice('Campeonato Brasileiro', value='campeonato-brasileiro'), 
    Choice('Copa do Brasil', value='copa-do-brasil')
]
lst_divison = [
    Choice('Serie A', value='a'), 
    Choice('Serie B', value='b'), 
    Choice('Serie C', value='c'), 
    Choice('Serie D', value='d')
]
lst_season = [str(year) for year in range(2012, 2022)]
lst_file_format = [
    Choice('json'), 
    Choice('xml'), 
    Choice('csv'),
    Choice('database')
]

#---------------------------------- Main method
@click.command()
def main(competition=None, division=None, season=None, file_format=None, sample=False):
    """Brazillian Football Web Scrapper - CLI"""
    print("+", "-" * 40, "+")
    print("|", " " * 40, "|")
    print("|", "Brazillian Football Web Scrapper - CLI".center(40), "|")
    print("|", " " * 40, "|")
    print("+", "-" * 40, "+\n")
    
    if not all((division, season, file_format)):
        competition = questionary.select(
            "Select a competition", 
            choices=lst_competition
        ).ask()
        division = questionary.select(
            "Select a division", 
            choices=lst_divison
        ).skip_if(competition == 'copa-do-brasil', default='a').ask()
        season = questionary.select(
            "Select a season", 
            choices=lst_season
        ).ask()
        is_all_games = questionary.confirm("Download all the games?").ask()
        file_format = questionary.select(
            "Select a file format for exporter function", 
            choices=lst_file_format
        ).ask()

        logging.info('Start of scrapping.')
        logging.info('Scrapping set to %s, %s, %s.', competition, division, season)
        scrapper(bfgame_queue, competition, division, season, is_all_games)
        logging.info('End of scrapping.')
        logging.info('Start of exporting.')
        exporter(bfgame_queue, competition, division, season, file_format)
        logging.info('End of exporting.')
    
    else:
        logging.info('Start of scrapping.')
        logging.info('Scrapping set to %s, %s, %s.', competition, division, season)
        scrapper(bfgame_queue, competition, str(division).lower(), season, sample)
        logging.info('End of scrapping.')
        logging.info('Start of exporting.')
        exporter(bfgame_queue, competition, str(division).lower(), season, file_format)
        logging.info('End of exporting.')

#---------------------------------- Entry point
if __name__ == '__main__':
    set_logger()
    main()