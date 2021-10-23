import os
import csv
import zipfile
import logging
from src.utils import timestamp_decorator
from pymongo import MongoClient


#---------------------------------- Game exporter function
@timestamp_decorator
def exporter(gameq: list, competition: str, division: str, season: str, file_format: str):

    file_name = f'{competition}-{season}' if competition == 'copa-do-brasil' else f'{competition}-{division}-{season}'

    if file_format == 'json': 
        with zipfile.ZipFile(
                            os.path.join(os.getcwd(), 'export', f'{file_name}.zip'), 
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

                except:
                    logging.exception('Permission error on saving JSON file.')
    
    elif file_format == 'xml':
        with zipfile.ZipFile(
                            os.path.join(os.getcwd(), 'export', f'{file_name}.zip'), 
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

                except:
                    logging.exception('Permission error on saving XML file.' )

    elif file_format == 'csv':            
        with open(
                os.path.join(os.getcwd(), 'export', f'{file_name}.csv'), 
                'w', 
                encoding='utf-8', 
                newline='') as csv_file:
            try:
                writer = csv.writer(csv_file, delimiter=';')                              
                for index, game in enumerate(gameq):
                    if index == 0:
                        writer.writerow(game.get_game_csv()[0])
                    writer.writerow(game.get_game_csv()[1])
            except:
                logging.exception('Permission error on saving CSV file.')
    
    else: # Database must be MongoDB
        db_uri = 'mongodb://localhost:27017/'
        with MongoClient(db_uri) as mongo_client:
            db = mongo_client["football"]
            collection = db[f"{competition}-{division}"]
            try:                              
                for game in gameq:
                    collection.insert_one(game.get_game_dict())
            except:
                logging.exception('Error on saving data into database.')

    print(f' Games downloaded: {len(gameq)}')
    print(' Check out the .export/ directory.')