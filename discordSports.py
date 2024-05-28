import requests
import discord
import json

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

apiKey = 'f1d76feac25888d8537426383355d480'

def get_event_id(team):
    url = f'https://api.the-odds-api.com/v4/sports/basketball_nba/events?regions=us&oddsFormat=american&apiKey={apiKey}'

    response = requests.get(url)
    event_ids = []
    main_event = response.json()
    
    for event in main_event:
        if event['home_team'][:3].lower() == team:
            event_ids.append(event['id'])
    
    for event in main_event:
        if event['away_team'][:3].lower() == team:
            event_ids.append(event['id'])
    
    return event_ids

def player_web(event_ids, stat):
    
    def listToString(s):

        # initialize an empty string
        str1 = ""
        # traverse in the string
        for ele in s:
            str1 += ele
        # return string
        return str1
    
    event_ids = (listToString(event_ids))
    
    global bstat  # use the global variable bstat
    
    bstat = 'a'

    if stat == 0:
        bstat = 'player_points'
    elif stat == 1:
        bstat = 'player_rebounds'
    elif stat == 2:
        bstat = 'player_assists'
    elif stat == 3:
        bstat = 'player_threes'
    elif stat == 4:
        bstat = 'player_blocks'
    elif stat == 5:
        bstat = 'player_steals'
    elif stat == 6:
        bstat = 'player_turnovers'
    elif stat == 7:
        bstat = 'player_points_rebounds_assists'
    elif stat == 8:
        bstat = 'player_points_rebounds'
    elif stat == 9:
        bstat = 'player_points_assists'
    elif stat == 10:
        bstat = 'player_rebounds_assists'

    url2 = f'https://api.the-odds-api.com/v4/sports/basketball_nba/events/{event_ids}/odds?apiKey={apiKey}&bookmakers=pinnacle&markets={bstat}&oddsFormat=american'
    
    responsedata = requests.get(url2)
    json_data = responsedata.json()
    
    return json_data

def find_normal_odds(playerdata):
    player_odds = {}
    for bookmaker in playerdata['bookmakers']:
        for market in bookmaker['markets']:
            for outcome in market['outcomes']:
                if outcome['description'] not in player_odds:
                    player_odds[outcome['description']] = {}
                if outcome['name'] == 'Over':
                    player_odds[outcome['description']]['over'] = outcome['price']
                elif outcome['name'] == 'Under':
                    player_odds[outcome['description']]['under'] = outcome['price']
    return player_odds


def find_novig_odds(player_odds2):
    player_no_vig_odds_names = []
    
    for player, odds in player_odds2.items():
        over_odds = odds['over']
        under_odds = odds['under']
        
        if over_odds > 0:
            over_implied_prob = 1/(over_odds/100+1)
        else:
            over_implied_prob = 1/(1+100/abs(over_odds))
        if under_odds > 0:
            under_implied_prob = 1/(under_odds/100+1)
        elif under_odds < 0:
            under_implied_prob = 1/(1+100/(abs(under_odds)))
        
        #Sum with vig
        sum_odds = under_implied_prob + over_implied_prob
        
        #remove vig
        over_implied_prob_novig = over_implied_prob/sum_odds
        under_implied_prob_novig = under_implied_prob/sum_odds
        
        if over_implied_prob_novig >= 0.5773502692:
            player_no_vig_odds_names.append(f"{player}")
        if under_implied_prob_novig >= 0.5773502692:
            player_no_vig_odds_names.append(f"{player}")
    return player_no_vig_odds_names


def find_bets(names_ofbet, playerdata):
    matching_outcomes = []
    #http://cissandbox.bentley.edu/sandbox/wp-content/uploads/2022-02-10-Documentation-on-f-strings-Updated.pdf
    for bookmaker in playerdata['bookmakers']:
        for market in bookmaker['markets']:
            for outcome in market['outcomes']:
                for person in names_ofbet:
                    if outcome['description'] == person:
                        if outcome['name'] == "Under":
                            matching_outcomes.append(f"--{outcome['description']:^25}-- \n  U {outcome['point']} ⬇\n {bookmaker['title']}:{outcome['price']} \n")
                        if outcome['name'] == "Over":
                            matching_outcomes.append(f"--{outcome['description']:^25}-- \n  O {outcome['point']} ⬆\n {bookmaker['title']}:{outcome['price']} \n")

    return matching_outcomes

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!props'):
        await message.channel.send('Received !props command')
        team = message.content[7:10]
        realid = get_event_id(team)
        if not realid:
            await message.channel.send('This event does not exist currently')
        else:
            for stat in range(10):
                playerdata = player_web(realid, stat)
                await message.channel.send(f'****{bstat}****')
                player_odds2 = find_normal_odds(playerdata)
                names_ofbet = find_novig_odds(player_odds2)
                outcomes2 = find_bets(names_ofbet, playerdata)
                for outcome in outcomes2:
                    await message.channel.send(outcome)
        await message.channel.send('I have found all opportunities')
    else:
        await message.channel.send('Improper format')


client.run('MTA4OTA1MjczOTcxMzExMDA0Ng.G94JpV.zYKw28gIb_-wIe_TpRi_2sA4swmIjYMK4JzRZc')




