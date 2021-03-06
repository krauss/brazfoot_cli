import json
import logging
import xml.etree.ElementTree as ET
from .utils import parse_datetime
from bs4 import Tag, BeautifulSoup

#===========================================================================
#                        GameCampeonatoBrasileiro Class 
#===========================================================================
class GameCampeonatoBrasileiro:

    def __init__(self, soup: BeautifulSoup, date_mode: str):
        self.competition_header = self.extract_competition_header(soup)
        self.game_header = self.extract_game_header(soup, date_mode)
        lineup = self.extract_lineup(soup)
        self.game_score =  self.extract_game_info(soup, lineup) 
        self.game_referees = self.extract_game_referees(soup)

    #-------------------------------------------------------------------------
    def extract_competition_header(self, soup: BeautifulSoup) -> dict:
        '''Method gets a soup as argument and returns a dict with competition name and game number'''
        result = {}

        competition_header = soup.find(class_='section-placar-header')

        if competition_header:

            try:
                competition_name = str(competition_header.find('h3').text).strip()
            except Exception as ex:
                logging.warning('Error: game has no competition name. Setting to None. %s', ex)
                result['competition'], result['division'], result['season'] = (None, None, None)
            else:
                result['competition'], result['division'], result['season'] = tuple(competition_name.split(' - '))

            try:
                competition_game_number = str(competition_header.findAll('span')[-1].text).strip()
                competition_game_number = str(competition_game_number).split(':')[-1]
            except Exception as ex:
                logging.critical(f'Error: game has no number. Setting to -1. %s', ex)
                result['game'] = -1
            else:
                result['game'] = int(competition_game_number)

        return result

    #-------------------------------------------------------------------------
    def extract_game_header(self, soup: BeautifulSoup, date_mode: str) -> dict:
        '''Method gets a soup as argument and returns a dict with game date and place'''
        result = {}    

        game_header = soup.find(class_='section-content-header')

        if game_header:                       
            game_header_local = str(game_header.findAll('span')[0].text).split(' - ')
            try:
                game_header_stadium = str(game_header_local[0]).strip()
            except:
                logging.warning(f'Game {self.competition_header["game"]} has no stadium information. Setting it to None.')
                game_header_stadium = None                
            
            try:
                game_header_city = str(game_header_local[1]).strip()
            except:
                logging.warning(f'Game {self.competition_header["game"]} has no city information. Setting it to None.')
                game_header_city = None

            try:
                game_header_state = str(game_header_local[2]).strip()
            except:
                logging.warning(f'Game {self.competition_header["game"]} has no state information. Setting it to None.')
                game_header_state = None

            try:
                game_header_date = game_header.findAll('span')[1].text
            except:
                logging.warning(f'Game {self.competition_header["game"]} has no date information. Setting it to None.')
                game_header_date = None
            
            try:
                game_header_time = game_header.findAll('span')[2].text
            except:
                logging.warning(f'Game {self.competition_header["game"]} has no time information. Setting it to None.')
                game_header_time = None

            try:
                game_header_channel = game_header.findAll('span')[3].text
            except:
                logging.warning(f'Game {self.competition_header["game"]} has no channel information. Setting it to None.')
                game_header_channel = None

            result['local'] = {'stadium': game_header_stadium, 
                            'city': game_header_city, 
                            'state': game_header_state, 
                            'channel': game_header_channel}
            result['datetime'] = parse_datetime(game_header_date, game_header_time, mode=date_mode)

        return result

    #-------------------------------------------------------------------------
    def extract_lineup(self, soup: BeautifulSoup) -> dict:
        lineup = {}

        game_players = soup.find(id='escalacao')

        try:
            for index, list_item in enumerate(game_players.findAll('ul'), start=1): 
                player_list = []

                for i in list_item.children:
                    info = []
                    obs = []
                    goals = []

                    if type(i) == Tag:
                    
                        for item in i.findAll('i'):

                            if 'icon-yellow-card' in item.get('class'):
                                obs.append('yellow card')                        
                            elif 'icon-red-card' in item.get('class'):
                                obs.append('red card')
                            elif item.find('path').get('fill') == '#FA1200':
                                obs.append('out')
                            elif item.find('path').get('fill') == '#399C00':
                                obs.append('in')
                            else:
                                goals.append(str(item.get('title')))

                        tmp = tuple(str(i.text).split())
                        info.append(tmp[0]) # player number
                        info.append(' '.join(tmp[1:])) # player name
                        if goals:
                            info.append(','.join(goals)) # player goals
                        if obs:
                            info.append(','.join(obs)) # player cards and substituition

                        player_list.append(','.join(info))

                lineup[f'{index}'] = player_list
        except Exception as ex:
            logging.critical('Team has no lineup definition. Setting to None. %s', ex)
            
        return lineup

    #-------------------------------------------------------------------------
    def extract_game_info(self, soup: BeautifulSoup, lineup: dict) -> dict:
        result = {}
        game_canceled = soup.find(class_='cancelado')
        game_score =  soup.find(class_='placar-wrapper')
        #--------- Home team info
        home_team = game_score.find(class_='time-left')
        home_team_name = home_team.find(class_='time-nome').text
        if not game_canceled:
            home_team_goals = home_team.find(class_='time-gols').text
            home_team_goals = int(home_team_goals)    
        #--------- Away team info
        away_team = game_score.find(class_='time-right')
        away_team_name = away_team.find(class_='time-nome').text
        if not game_canceled:
            away_team_goals = away_team.find(class_='time-gols').text
            away_team_goals = int(away_team_goals)
        #--------- Check for penalty goals
        home_team_penalty_goals = 0
        away_team_penalty_goals = 0
        penalti_score = game_score.find(class_="x center-block").find_all("strong")
        if penalti_score:
            home_team_penalty_goals = int(penalti_score[0].text)
            away_team_penalty_goals = int(penalti_score[1].text)

        if not game_canceled:
            if (home_team_goals + home_team_penalty_goals) > (away_team_goals + away_team_penalty_goals):
                winner = home_team_name
            elif (away_team_goals + away_team_penalty_goals) > (home_team_goals + home_team_penalty_goals):
                winner = away_team_name
            else:
                winner = None

            result['winner'] = winner
            result['home'] = {
                'name': home_team_name, 
                'goals': home_team_goals,
                'penalties': home_team_penalty_goals if home_team_penalty_goals else None,
                'lineup': lineup.get('1'), 
                'substitutes': lineup.get('3')
            }
            result['away']= {
                'name': away_team_name, 
                'goals': away_team_goals,
                'penalties': away_team_penalty_goals if away_team_penalty_goals else None,
                'lineup': lineup.get('2'), 
                'substitutes': lineup.get('4')
            }

        else:
            logging.critical('Game %s has been canceled.', self.competition_header["game"])
            result['winner'] = 'Canceled'
            result['home'] = {
                'name': home_team_name
            }
            result['away']= {
                'name': away_team_name
            }

        return result

    #-------------------------------------------------------------------------
    def extract_game_referees(self, soup: BeautifulSoup) -> dict:
        '''Extract and returns a list of Referees'''
        referees = []
        game_referees = soup.find(id='arbitros').find(class_='table').find('tbody').findAll('tr')

        if game_referees:
            for row in game_referees:            
                referees.append(','.join([str(x.text).strip() for x in row.children if type(x) == Tag]))

        return {'referees': referees}

    #-------------------------------------------------------------------------
    def get_game_dict(self) -> dict:
        '''Return this Game object as a dictionary. Suitable to use with document-based No-SQL databases like MongoDB'''
        return self.competition_header | self.game_header | self.game_score | self.game_referees

    #-------------------------------------------------------------------------
    def get_game_json(self):
        '''Return this Game object as a JSON'''
        game = self.get_game_dict()

        return json.dumps(game, ensure_ascii=False, indent=4)

    #-------------------------------------------------------------------------
    def get_game_xml(self) -> ET.ElementTree:
        '''Return this Game object as a XML'''
        game = ET.Element('game')
        competition = ET.SubElement(game, 'competition')
        competition.text = self.competition_header['competition']
        division = ET.SubElement(game, 'division')
        division.text = self.competition_header['division']
        edition = ET.SubElement(game, 'season')
        edition.text = self.competition_header['season']
        game_number = ET.SubElement(game, 'game')
        game_number.text = str(self.competition_header['game'])

        local = ET.SubElement(game, 'local')
        stadium = ET.SubElement(local, 'stadium')
        stadium.text = self.game_header['local']['stadium']
        city = ET.SubElement(local, 'city')
        city.text = self.game_header['local'].get('city', '')
        state = ET.SubElement(local, 'state')
        state.text = self.game_header['local'].get('state', '')
        channel = ET.SubElement(local, 'channel')
        channel.text = self.game_header['local'].get('channel', '')
        date_time = ET.SubElement(game, 'datetime')
        date_time.text = str(self.game_header['datetime'])
        winner = ET.SubElement(game, 'winner')
        winner.text = self.game_score['winner']
        #------------ HOME -------------------------------------
        home = ET.SubElement(game, 'home')
        hname = ET.SubElement(home, 'name')
        hname.text = self.game_score['home']['name']
        hgoals = ET.SubElement(home, 'goals')
        hgoals.text = str(self.game_score['home'].get('goals', ''))

        hlineup = ET.SubElement(home, 'lineup')
        if self.game_score['home'].get('lineup'):
            for player in self.game_score['home']['lineup']:
                pl = ET.SubElement(hlineup, 'player')
                vals = player.split(',')
                attributes = {}
                attributes['number'] = vals[0] # Player number

                if len(vals) > 2:
                    for obs in vals[2:]:
                        if obs in ('in', 'out'):
                            attributes['obs'] = obs
                        elif obs in ('red card', 'yellow card'):
                            attributes['cards'] = obs
                        else:
                            attributes['goals'] = obs
                
                pl.attrib = attributes
                pl.text = vals[1] # Player name
        else:
            hlineup.text = ""

        hsubs = ET.SubElement(home, 'substitutes')
        if self.game_score['home'].get('substitutes'):
            for player in self.game_score['home']['substitutes']:
                pl = ET.SubElement(hsubs, 'player')
                vals = player.split(',')
                pl.attrib = {'number': vals[0]}
                pl.text = vals[1]
        else:
            hsubs.text = ""
        #------------ AWAY -------------------------------------
        away = ET.SubElement(game, 'away')
        aname = ET.SubElement(away, 'name')
        aname.text = self.game_score['away']['name']
        agoals = ET.SubElement(away, 'goals')
        agoals.text = str(self.game_score['away'].get('goals', ''))
        
        alineup = ET.SubElement(away, 'lineup')
        if self.game_score['away'].get('lineup'):
            for player in self.game_score['away']['lineup']:
                pl = ET.SubElement(alineup, 'player')
                vals = player.split(',')
                attributes = {}
                attributes['number'] = vals[0] # Player number

                if len(vals) > 2:
                    for obs in vals[2:]:
                        if obs in ('in', 'out'):
                            attributes['obs'] = obs
                        elif obs in ('red card', 'yellow card'):
                            attributes['cards'] = obs
                        else:
                            attributes['goals'] = obs
                
                pl.attrib = attributes
                pl.text = vals[1] # Player name
        else:
            hlineup.text = ""

        asubs = ET.SubElement(away, 'substitutes')
        if self.game_score['away'].get('substitutes'):
            for player in self.game_score['away']['substitutes']:
                pl = ET.SubElement(asubs, 'player')
                vals = player.split(',')
                pl.attrib = {'number': vals[0]}
                pl.text = vals[1]
        else:
            asubs.text = ""        
        #------------ REFEREES -------------------------------------
        referees = ET.SubElement(game, 'referees')
        if self.game_referees['referees']:
            for line in self.game_referees['referees']:
                ref = ET.SubElement(referees, 'referee')
                vals = line.split(',')
                attributes = {}
                attributes['role'] = vals[0]
                if len(vals) > 2:
                    ref.text = vals[1]
                    attributes['category'] = vals[2]
                    attributes['federation'] = vals[3]
                ref.attrib = attributes
                


        return ET.ElementTree(game)
    
    #-------------------------------------------------------------------------
    def get_game_csv(self):
        '''Return a tuple containing the header and game object as a CSV'''
        header = ["competition", "division", "season", "game", 
                "stadium", "city", "state", "channel", "datetime", 
                "winner", "home_name", "home_goals", "away_name", 
                "away_goals"]
        
        game = {**self.competition_header}
        game |= self.game_header['local']
        game['datetime'] = self.game_header['datetime']
        game['winner'] = self.game_score['winner']
        game['home_name'] = self.game_score['home']['name']
        game['home_goals'] = self.game_score['home'].get('goals', '')
        game['away_name'] = self.game_score['away']['name']
        game['away_goals'] = self.game_score['away'].get('goals', '')

        return [hdr.upper() for hdr in header], game.values()
    
    #-------------------------------------------------------------------------
    def __str__(self) -> str:
        return f"game_{self.competition_header['game']}"

    #-------------------------------------------------------------------------
    def __repr__(self):
        return r"game_" + str(self.competition_header['game'])


#===========================================================================
#                        GameCopaDoBrasil Class 
#===========================================================================
class GameCopaDoBrasil:

    def __init__(self, soup: BeautifulSoup, date_mode: str):
        self.competition_header = self.extract_competition_header(soup)
        self.game_header = self.extract_game_header(soup, date_mode)
        lineup = self.extract_lineup(soup)
        self.game_score =  self.extract_game_info(soup, lineup) 
        self.game_referees = self.extract_game_referees(soup)

    #-------------------------------------------------------------------------
    def extract_competition_header(self, soup: BeautifulSoup) -> dict:
        '''Method gets a soup as argument and returns a dict with competitio name and game number'''
        result = {}

        competition_header = soup.find(class_='section-placar-header')

        if competition_header:
            competition_name = str(competition_header.find('h3').text).strip()
            competition_game_number = str(competition_header.findAll('span')[-1].text).strip()
            competition_game_phase, competition_game_group, competition_game_number = tuple(str(competition_game_number).split(' | '))

            result['competition'], result['season'] = tuple(competition_name.split(' - '))
            result['phase'] = competition_game_phase
            result['group'] = competition_game_group.split()[-1]
            result['game'] = int(competition_game_number.split()[-1])

        return result

    #-------------------------------------------------------------------------
    def extract_game_header(self, soup: BeautifulSoup, date_mode: str) -> dict:
        '''Method gets a soup as argument and returns a dict with game date and place'''
        result = {}    

        game_header = soup.find(class_='section-content-header')

        if game_header:
            game_header_local = str(game_header.findAll('span')[0].text).split(' - ')
            game_header_stadium = str(game_header_local[0]).strip()
            try:            
                game_header_city = str(game_header_local[1]).strip()
                game_header_state = str(game_header_local[2]).strip()
            except IndexError:
                game_header_city = game_header_state = ''

            game_header_date = game_header.findAll('span')[1].text
            game_header_time = game_header.findAll('span')[2].text
            try:
                game_header_channel = game_header.findAll('span')[3].text
            except IndexError:
                game_header_channel = ''

            result['local'] = {'stadium': game_header_stadium, 
                            'city': game_header_city, 
                            'state': game_header_state, 
                            'channel': game_header_channel}
            result['datetime'] = parse_datetime(game_header_date, game_header_time, mode=date_mode)

        return result

    #-------------------------------------------------------------------------
    def extract_lineup(self, soup: BeautifulSoup) -> dict:
        lineup = {}

        game_players = soup.find(id='escalacao')

        if game_players:
            for index, list_item in enumerate(game_players.findAll('ul'), start=1): 
                player_list = []

                for i in list_item.children:
                    info = []
                    obs = []
                    goals = []

                    if type(i) == Tag:
                    
                        for item in i.findAll('i'):

                            if 'icon-yellow-card' in item.get('class'):
                                obs.append('yellow card')                        
                            elif 'icon-red-card' in item.get('class'):
                                obs.append('red card')
                            elif item.find('path').get('fill') == '#FA1200':
                                obs.append('out')
                            elif item.find('path').get('fill') == '#399C00':
                                obs.append('in')
                            else:
                                goals.append(str(item.get('title')))

                        tmp = tuple(str(i.text).split())
                        info.append(tmp[0]) # player number
                        info.append(' '.join(tmp[1:])) # player name
                        if goals:
                            info.append(','.join(goals)) # player goals
                        if obs:
                            info.append(','.join(obs)) # player cards and substituition

                        player_list.append(','.join(info))

                lineup[f'{index}'] = player_list
            
        return lineup

    #-------------------------------------------------------------------------
    def extract_game_info(self, soup: BeautifulSoup, lineup: dict) -> dict:
        result = {}
        game_canceled = soup.find(class_='cancelado')
        game_score =  soup.find(class_='placar-wrapper')
        #--------- Home team info
        home_team = game_score.find(class_='time-left')
        home_team_name = home_team.find(class_='time-nome').text
        if not game_canceled:
            home_team_goals = home_team.find(class_='time-gols').text
            home_team_goals = int(home_team_goals)
        #--------- Away team info
        away_team = game_score.find(class_='time-right')
        away_team_name = away_team.find(class_='time-nome').text
        if not game_canceled:
            away_team_goals = away_team.find(class_='time-gols').text
            away_team_goals = int(away_team_goals)
        #--------- Check for penalty goals
        home_team_penalty_goals = 0
        away_team_penalty_goals = 0
        penalti_score = game_score.find(class_="x center-block").find_all("strong")
        if penalti_score:
            home_team_penalty_goals = int(penalti_score[0].text)
            away_team_penalty_goals = int(penalti_score[1].text)

        if not game_canceled:            
            try:
                if (home_team_goals + home_team_penalty_goals) > (away_team_goals + away_team_penalty_goals):
                    winner = home_team_name
                elif (away_team_goals + away_team_penalty_goals) > (home_team_goals + home_team_penalty_goals):
                    winner = away_team_name
                else:
                    winner = None
            except ValueError:
                winner = None

            result['winner'] = winner
            result['home'] = {
                'name': home_team_name, 
                'goals': home_team_goals if home_team_goals else None,
                'penalties': home_team_penalty_goals if home_team_penalty_goals else None,
                'lineup': lineup.get('1'), 
                'substitutes': lineup.get('3')
            }
            result['away']= {
                'name': away_team_name, 
                'goals': away_team_goals if away_team_goals else None,
                'penalties': away_team_penalty_goals if away_team_penalty_goals else None,
                'lineup': lineup.get('2'), 
                'substitutes': lineup.get('4')
            }

        else:
            result['winner'] = 'Canceled'
            result['home'] = {
                'name': home_team_name
            }
            result['away']= {
                'name': away_team_name
            }

        return result

    #-------------------------------------------------------------------------
    def extract_game_referees(self, soup: BeautifulSoup) -> dict:
        '''Extract and returns a list of Referees'''
        referees = []
        game_referees = soup.find(id='arbitros').find(class_='table').find('tbody').findAll('tr')

        if game_referees:
            for row in game_referees:            
                referees.append(','.join([str(x.text).strip() for x in row.children if type(x) == Tag]))

        return {'referees': referees}

    #-------------------------------------------------------------------------
    def get_game_dict(self) -> dict:
        '''Return this Game object as a dictionary. Suitable to use with document-based No-SQL databases like MongoDB'''
        return self.competition_header | self.game_header | self.game_score | self.game_referees

    #-------------------------------------------------------------------------
    def get_game_json(self):
        '''Return this Game object as a JSON'''
        game = self.get_game_dict()

        return json.dumps(game, ensure_ascii=False, indent=4)

    #-------------------------------------------------------------------------
    def get_game_xml(self) -> ET.ElementTree:
        '''Return this Game object as a XML'''
        game = ET.Element('game')
        competition = ET.SubElement(game, 'competition')
        competition.text = self.competition_header['competition']
        phase = ET.SubElement(game, 'phase')
        phase.text = self.competition_header['phase']
        group = ET.SubElement(game, 'group')
        group.text = self.competition_header['group']
        edition = ET.SubElement(game, 'season')
        edition.text = self.competition_header['season']
        game_number = ET.SubElement(game, 'game')
        game_number.text = str(self.competition_header['game'])

        local = ET.SubElement(game, 'local')
        stadium = ET.SubElement(local, 'stadium')
        stadium.text = str(self.game_header['local']['stadium'])
        city = ET.SubElement(local, 'city')
        city.text = self.game_header['local'].get('city', '')
        state = ET.SubElement(local, 'state')
        state.text = self.game_header['local'].get('state', '')
        channel = ET.SubElement(local, 'channel')
        channel.text = self.game_header['local'].get('channel', '')
        date_time = ET.SubElement(game, 'datetime')
        date_time.text = str(self.game_header['datetime'])

        winner = ET.SubElement(game, 'winner')
        winner.text = self.game_score['winner']
        #------------ HOME -------------------------------------
        home = ET.SubElement(game, 'home')
        hname = ET.SubElement(home, 'name')
        hname.text = self.game_score['home']['name']
        hgoals = ET.SubElement(home, 'goals')
        hgoals.text = str(self.game_score['home'].get('goals', ''))
        hlineup = ET.SubElement(home, 'lineup')

        if self.game_score['home'].get('lineup'):
            for player in self.game_score['home']['lineup']:
                pl = ET.SubElement(hlineup, 'player')
                vals = player.split(',')
                attributes = {}
                attributes['number'] = vals[0] # Player number

                if len(vals) > 2:
                    for obs in vals[2:]:
                        if obs in ('in', 'out'):
                            attributes['obs'] = obs
                        elif obs in ('red card', 'yellow card'):
                            attributes['cards'] = obs
                        else:
                            attributes['goals'] = obs
                
                pl.attrib = attributes
                pl.text = vals[1] # Player name
        else:
            hlineup.text = ""

        hsubs = ET.SubElement(home, 'substitutes')
        if self.game_score['home'].get('substitutes'):
            for player in self.game_score['home']['substitutes']:
                pl = ET.SubElement(hsubs, 'player')
                vals = player.split(',')
                pl.attrib = {'number': vals[0]}
                pl.text = vals[1]
        else:
            hsubs.text = ""

        #------------ AWAY -------------------------------------
        away = ET.SubElement(game, 'away')
        aname = ET.SubElement(away, 'name')
        aname.text = self.game_score['away']['name']
        agoals = ET.SubElement(away, 'goals')
        agoals.text = str(self.game_score['away'].get('goals', ''))
        alineup = ET.SubElement(away, 'lineup')

        if self.game_score['away'].get('lineup'):
            for player in self.game_score['away']['lineup']:
                pl = ET.SubElement(alineup, 'player')
                vals = player.split(',')
                attributes = {}
                attributes['number'] = vals[0] # Player number

                if len(vals) > 2:
                    for obs in vals[2:]:
                        if obs in ('in', 'out'):
                            attributes['obs'] = obs
                        elif obs in ('red card', 'yellow card'):
                            attributes['cards'] = obs
                        else:
                            attributes['goals'] = obs
                
                pl.attrib = attributes
                pl.text = vals[1] # Player name
        else:
            hlineup.text = ""

        asubs = ET.SubElement(away, 'substitutes')
        if self.game_score['away'].get('substitutes'):
            for player in self.game_score['away']['substitutes']:
                pl = ET.SubElement(asubs, 'player')
                vals = player.split(',')
                pl.attrib = {'number': vals[0]}
                pl.text = vals[1]
        else:
            asubs.text = ""
        #------------ REFEREES -------------------------------------
        referees = ET.SubElement(game, 'referees')
        if self.game_referees['referees']:
            for line in self.game_referees['referees']:
                ref = ET.SubElement(referees, 'referee')
                vals = line.split(',')
                attributes = {}
                attributes['role'] = vals[0]
                if len(vals) > 2:
                    ref.text = vals[1]
                    attributes['category'] = vals[2]
                    attributes['federation'] = vals[3]
                ref.attrib = attributes
                


        return ET.ElementTree(game)
    
    #-------------------------------------------------------------------------
    def get_game_csv(self):
        '''Return a tuple containing the header and game object as a CSV'''
        header = ["competition", "season", "phase", "group", "game", 
                "stadium", "city", "state", "channel", "datetime", 
                "winner", "home_name", "home_goals", "away_name", 
                "away_goals"]
        
        game = {**self.competition_header}
        game |= self.game_header['local']
        game['datetime'] = self.game_header['datetime']
        game['winner'] = self.game_score['winner']
        game['home_name'] = self.game_score['home']['name']
        game['home_goals'] = self.game_score['home'].get('goals', '')
        game['away_name'] = self.game_score['away']['name']
        game['away_goals'] = self.game_score['away'].get('goals', '')

        return [hdr.upper() for hdr in header], game.values()
    
    #-------------------------------------------------------------------------
    def __str__(self):
        return f"game_{self.competition_header['game']}"

    #-------------------------------------------------------------------------
    def __repr__(self):
        return r"game_" + str(self.competition_header['game'])