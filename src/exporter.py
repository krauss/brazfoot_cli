import click
import os
import csv
import zipfile
from utils import timestamp_decorator

#---------------------------------- Game exporter function
@timestamp_decorator
def exporter(gameq, competition, division, season, is_all_games, file_format):

    if file_format == 'json': 
        with zipfile.ZipFile(
                            os.path.join(os.getcwd(), 'export', 'games.zip'), 
                            "w", 
                            compression=zipfile.ZIP_BZIP2, 
                            compresslevel=9) as zip_file:
            for game in gameq:
                try:
                    # Write the json file
                    with open(
                            os.path.join(os.getcwd(), 'export', f'{game}.json'), 
                            'w', 
                            encoding='utf-8') as json_file:
                        json_file.write(game.get_game_json())
                    
                    # Add it to the zil file
                    zip_file.write(os.path.join(os.getcwd(), 'export', f'{game}.json'), arcname=f'{game}.json')

                    # Remove the previous json file
                    os.remove(os.path.join(os.getcwd(), 'export', f'{game}.json'))

                except OSError as err:
                    print(f'Error: permission error {os.strerror(err.errno)}, stack_trace: {err.with_traceback()}')
    
    elif file_format == 'xml':
        with zipfile.ZipFile(
                            os.path.join(os.getcwd(), 'export', 'games.zip'), 
                            "w", 
                            compression=zipfile.ZIP_BZIP2, 
                            compresslevel=9) as zip_file:
            for game in gameq:
                try:
                    # Write the xml file
                    game.get_game_xml().write(
                                            os.path.join(os.getcwd(), 'export', f'{game}.xml'), 
                                            encoding='utf-8', 
                                            method='xml', 
                                            xml_declaration=True)
                    
                    # Add it to the xip file 
                    zip_file.write(
                                    os.path.join(os.getcwd(), 'export', f'{game}.xml'), 
                                    arcname=f'{game}.xml')

                    # Remove the previous json file
                    os.remove(os.path.join(os.getcwd(), 'export', f'{game}.xml'))

                except OSError as err:
                    print(f'Error: permission error {os.strerror(err.errno)}, stack_trace: {err.with_traceback()}')                
    
    else:            
        with open(
                os.path.join(os.getcwd(), 'export', f'{competition}-{division}-{season}.csv'), 
                'w', 
                encoding='utf-8', 
                newline='') as csv_file:
            try:
                writer = csv.writer(csv_file, delimiter=';')                              
                for index, game in enumerate(gameq):
                    if index == 0:
                        writer.writerow(game.get_game_csv()[0])
                    writer.writerow(game.get_game_csv()[1])
            except PermissionError as err:
                print(f'Error: permission error {os.strerror(err.errno)}, stack_trace: {err.with_traceback()}')        

    print(f'Games downloaded: {len(gameq)}')
    print('Check out the .export/ directory.')