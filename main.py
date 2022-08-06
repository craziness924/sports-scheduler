from datetime import timedelta
import yaml
import round_robin_tournament as rrt

pairInfos = {}
validation = {}
teams = []
seasonMatches = []


with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

for team in config["teams"]:
    teams.append(team)
    
    teamShortCode = team["shortcode"]
    validation[teamShortCode] = {}
    validation[teamShortCode]["awayCounts"] = 0
    validation[teamShortCode]["homeCounts"] = 0

gapBetweenGames = config["dates"]["gapBetweenGames"]
gapBetweenWeeks = config["dates"]["gapBetweenWeeks"]

opponentCount = len(teams) - 1
gamesPerOpp = config["games"]["perTeam"] / opponentCount    

if (gamesPerOpp - int(gamesPerOpp) != 0):
    print(f"Invalid number of games! Games per opponent: {gamesPerOpp}")
    exit(1)

pairs = rrt.Tournament(teams).get_active_matches()
for pair in pairs:
    pairInfo = {}
    participants = pair.get_participants()
    left_team = participants[0].get_competitor()
    right_team = participants[1].get_competitor()

    pairInfo["left"] = left_team
    pairInfo["right"] = right_team
    pairInfo["leftHome"] = False

    pairInfos[f"{left_team['shortcode']}_{right_team['shortcode']}"] = pairInfo

weekStartDate = config["dates"]["start"]
for x in range(0, int(gamesPerOpp)):
    week = rrt.Tournament(teams)
    weekMatches = week.get_active_matches()

    gameDate = weekStartDate

    for x in range(0, len(weekMatches)):
        matchInfo = {}
        match = weekMatches[x]
        participants = match.get_participants()
        
        left_team = participants[0].get_competitor()
        right_team = participants[1].get_competitor()

        pair = pairInfos[f"{left_team['shortcode']}_{right_team['shortcode']}"]

        if pair["leftHome"]:
            matchInfo["away"] = right_team
            matchInfo["home"] = left_team
        else:
            matchInfo["away"] = left_team
            matchInfo["home"] = right_team

        matchInfo["date"] = gameDate
        matchInfo["venue"] = matchInfo["home"]["arena"]

        pair["leftHome"] = not pair["leftHome"]

        gameDate += timedelta(gapBetweenGames)
        seasonMatches.append(matchInfo)
    if config["weeklyGames"]:
        weekStartDate += timedelta(days=gapBetweenWeeks)
    else:
        gameDate += timedelta(days=gapBetweenGames)
        weekStartDate = gameDate
    
for match in seasonMatches:
    errors = False

    validation[match['away']['shortcode']]["awayCounts"] += 1
    validation[match['home']['shortcode']]["homeCounts"] += 1
    

    print(f"{match['date']}: {match['away']['shortcode']} @ {match['home']['shortcode']}")

for team in validation:
    if not ((validation[team]["awayCounts"] + validation[team]["homeCounts"]) == config["games"]["perTeam"]):
        Exception(f"{team} has an improper number of games!")
        exit(1)



