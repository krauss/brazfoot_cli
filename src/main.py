import click
import asyncio
from questionary import questionary, Choice
from scrapper import scrapper
from async_scrapper import async_scrapper
from exporter import exporter

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
        file_format = questionary.select("Select a file format for exporter function", choices=lst_file_format).ask()

        scrapper(bfgame_queue, competition, division, season, is_all_games)
        #loop = asyncio.get_event_loop()
        #loop.run_until_complete(async_scrapper(bfgame_queue, competition, division, season, is_all_games))
        exporter(bfgame_queue, competition, division, season, file_format)
    
    else:
        scrapper(bfgame_queue, competition, str(division).lower(), season, sample)
        exporter(bfgame_queue, competition, str(division).lower(), season, file_format)

#---------------------------------- Entry point
if __name__ == '__main__':
    main()