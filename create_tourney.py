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
                    "Time":"NA",
                    "Player(s)":player["Player or Team Name"],
                    "Opponent(s)": "BYE, due to tournament rules"
                    })

    while len(players_to_schedule) > 0:
        player = players_to_schedule.pop()
        if len(players_to_schedule) <= 0:
            scheduled_players.append(player)
            tournament.append({
                "Time": player["Available Times"],
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
                        # TODO add court time here
                        # TODO check players schedules in other events as well
                        players_to_schedule.remove(opponent)
                        scheduled_players.append(opponent)
                        scheduled_players.append(player)
                        tournament.append({
                                "Time" : str(joint_availability),
                                "Player(s)" : player["Player or Team Name"],
                                "Opponent(s)" : opponent["Player or Team Name"]
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

