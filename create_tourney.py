import os
import csv
from pprint import pprint

import datetime
import pytz
from dateutil.parser import parse

from tkinter import Tk
from tkinter.filedialog import askopenfilename


def setup_courts():
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename(title='Choose courts csv file...') # show an "Open" dialog box and return the path to the selected file

    with open(filename) as f:
         courts = [{k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)]

    return courts

def setup_players():
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename(title='Choose players csv file...') # show an "Open" dialog box and return the path to the selected file

    with open(filename) as f:
         players = [{k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)]

    return players

def setup_sports():
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename(title='Choose sports csv file...') # show an "Open" dialog box and return the path to the selected file
    
    with open(filename) as f:
        sports = [{k: v for k, v in row.items()}
            for row in csv.DictReader(f, skipinitialspace=True)]

    return sports

def setup_player_schedules(players):
    
    player_schedules={}

    #TODO look for people with the same name, this is currently not used
    for player in players:
        individual_names = [x.strip() for x in player['Player or Team Name'].split('+')]
        for name in individual_names:
            player_schedules[name]={}

    print(player_schedules)
    return player_schedules


def setup_court_schedules(courts):
    court_schedules = {}
    
    for court in courts:
        court_schedules[court['Court Name']] = {
                'sports' : [x.strip() for x in court['Sports'].split(',')],
                'open_time' : parse(court['Open Time'],ignoretz=True),
                'close_time' : parse(court['Close Time'],ignoretz=True),
                'events' : []
        }

    print(court_schedules)
    return court_schedules

def schedule_court(player, opponent, court_schedules, sport, duration, start_dt, end_dt, time_preference=[]):
    
    total_events = int(((end_dt-start_dt).total_seconds() / 60) / duration)
    for event_counter in range(total_events): 
        for court_name in court_schedules:
            events = court_schedules[court_name]['events']
            if sport in court_schedules[court_name]['sports'] and len(events) < event_counter:
                court_open = court_schedules[court_name]['open_time']
                court_close = court_schedules[court_name]['close_time']

                if 'anytime' in time_preference or 'early' in time_preference:
                    test_start = start_dt
                elif 'late' in time_preference:
                    test_start = start_dt.replace(hour=17)
                else:
                    test_start = start_dt

                test_start = test_start
                test_end = test_start + datetime.timedelta(minutes=duration)
                           
                while test_end < end_dt:
                    if len(events) == 0:
                        if test_start.time() > court_open.time() and test_end.time() < court_close.time():
                            return { 
                                'player': player["Player or Team Name"],
                                'opponent': opponent["Player or Team Name"],
                                'court_name': court_name,
                                'match_start' : test_start,
                                'match_end': test_end
                                }
                    else:
                        conflict = False
                        
                        for event in events:
                            if not (test_start.time() >= court_open.time() and test_end.time() <= court_close.time() and test_start <= event['match_start'] and test_start <= event['match_end'] and test_end <= event['match_start'] and test_end <= event['match_end']) and not (test_start.time() >= court_open.time() and test_end.time() <= court_close.time() and test_start >= event['match_start'] and test_start >= event['match_end'] and test_end >= event['match_start'] and test_end >= event['match_end']):
                                conflict = True

                        if conflict == False:
                            return { 
                                'player': player["Player or Team Name"],
                                'opponent': opponent["Player or Team Name"],
                                'court_name': court_name,
                                'match_start' : test_start,
                                'match_end': test_end
                                }
                    test_start = test_start + datetime.timedelta(minutes=5)
                    test_end = test_end + datetime.timedelta(minutes=5)
    return { 'court_name': 'failed' }


def main():
    sports = setup_sports()
    players = setup_players()
    courts = setup_courts()
    player_schedules = setup_player_schedules(players)    
    court_schedules = setup_court_schedules(courts)

    for sport in sports:
        tourney_title= sport["Sport"] + " Class " + sport["Class"]
        sport_name = sport["Sport"]
        class_name = sport["Class"]
        duration = int(sport["Time"])
        total_byes = int(sport["# Byes"])
        
        tourney_start = parse(sport['Tournament Start Date'] + ' ' +  sport['Tournament Start Time'],ignoretz=True)
        tourney_end = parse(sport['Tournament End Date'] + ' ' +  sport['Tournament End Time'],ignoretz=True)

        scheduled_byes = 0
        tournament = []

        sport_players = []
        for player in players:
            if player["Sport"] == sport_name and player["Class"] == class_name:
                sport_players.append(player)
        
        num_players=len(sport_players)
        num_players_to_schedule = num_players - total_byes
        players_to_schedule = sport_players 
        abandoned_players = []
        scheduled_players = []

        # TODO schedule byes only for the best players, need handicaps first
        if total_byes > len(players_to_schedule):
            for i in range(total_byes):
                player = players_to_schedule.pop()
                scheduled_players.append(player)
                tournament.append({
                        "Player(s)":player["Player or Team Name"],
                        "Opponent(s)": "BYE, due to tournament rules"
                        })

        while len(players_to_schedule) > 0:
            player = players_to_schedule.pop()
            if len(players_to_schedule) <= 0:
                scheduled_players.append(player)
                tournament.append({
                    "Player(s)":player["Player or Team Name"],
                    "Opponent(s)": "BYE, due to someone else's scheduling conflict or odd number of players"
                    })
            else: 
                scheduled = False
                for opponent in players_to_schedule:
                    if not scheduled:
                        player_availability = [x.strip() for x in player["Available Times"].split(',')]
                        opponent_availability = [x.strip() for x in opponent["Available Times"].split(',')]
                        joint_availability = set(player_availability) & set(opponent_availability)
                        if len(joint_availability) > 0:
                            court_event = schedule_court(player, opponent, court_schedules, sport_name, duration, tourney_start, tourney_end, joint_availability)
                            if 'failed' not in court_event['court_name']:
                                court_schedules[court_event['court_name']]['events'].append(court_event)
                                players_to_schedule.remove(opponent)
                                scheduled_players.append(opponent)
                                scheduled_players.append(player)
                                tournament.append({
                                    "Start" : court_event['match_start'],
                                    "End": court_event['match_end'],
                                    "Court" : court_event['court_name'],
                                    "Player(s)" : player["Player or Team Name"],
                                    "Opponent(s)" : opponent["Player or Team Name"],
                                    "Joint Availability" : str(joint_availability)
                                })
                                scheduled = True
                if not scheduled:
                    abandoned_players.append(player)
        
        print(tourney_title)
        print("📅")
        pprint(tournament)
        print("🛑")
        pprint(abandoned_players)
       
        # TODO let user select folder to save results to
        if len(tournament) > 0:
            with open(os.path.join('data','results',tourney_title+'.csv'),'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=tournament[0].keys())
                writer.writeheader()
                writer.writerows(tournament)
        if len(abandoned_players) > 0:
            with open(os.path.join('data','results',tourney_title+'ABANDONED.csv'),'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=abandoned_players[0].keys())
                writer.writeheader()
                writer.writerows(abandoned_players)

if __name__ == "__main__":
    main()
