import os
import csv
from pprint import pprint

sports = []
players = []

# TODO select these files instead of pick from data folder
with open(os.path.join('data','sports.csv')) as f:
    sports = [{k: v for k, v in row.items()}
        for row in csv.DictReader(f, skipinitialspace=True)]

with open(os.path.join('data','players.csv')) as f:
     players = [{k: v for k, v in row.items()}
        for row in csv.DictReader(f, skipinitialspace=True)]

for sport in sports:
    tourney_title= sport["Sport"] + " Class " + sport["Class"]
    sport_name = sport["Sport"]
    class_name = sport["Class"]
    length = int(sport["Time"])
    total_byes = int(sport["# Byes"])
    
    scheduled_byes = 0
    tournament = []

    sport_players = []
    for player in players:
        if player["Sport"] == sport_name and player["Class"] == class_name:
            sport_players.append(player)
    
    num_players=len(sport_players)
    players_to_schedule = sport_players 
    abandoned_players = []

    for player in sport_players:
        if len(players_to_schedule) == 0:
            continue
        elif scheduled_byes < total_byes:
            # TODO schedule byes only for the best players, need handicaps first
            players_to_schedule.remove(player)
            tournament.append({
                    "Time":"NA",
                    "Player(s)":player["Player or Team Name"],
                    "Opponent(s)": "BYE"
               })
            scheduled_byes += 1
        else: 
            players_to_schedule.remove(player)
            scheduled = False
            for opponent in players_to_schedule:
                if not scheduled:
                    player_availability = [x.strip() for x in player["Available Times"].split(',')]
                    opponent_availability = [x.strip() for x in opponent["Available Times"].split(',')]
                    joint_availability = set(player_availability) & set(opponent_availability)
                    if len(joint_availability) > 0:
                        # TODO add court time here

                        players_to_schedule.remove(opponent)
                        tournament.append({
                                "Time" : str(joint_availability),
                                "Player(s)" : player["Player or Team Name"],
                                "Opponent(s)" : opponent["Player or Team Name"]
                            })
                        scheduled = True
            if not scheduled:
                abandoned_players.append(player)
    
    # TODO save to file
    print(tourney_title)
    print("📅")
    pprint(tournament)
    print("🛑")
    pprint(abandoned_players)
    
    if len(tournament) > 0:
        with open(os.path.join('data',tourney_title+'.csv'),'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=tournament[0].keys())
            writer.writeheader()
            writer.writerows(tournament)
    if len(abandoned_players) > 0:
        with open(os.path.join('data',tourney_title+'ABANDONED.csv'),'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=abandoned_players[0].keys())
            writer.writeheader()
            writer.writerows(abandoned_players)

