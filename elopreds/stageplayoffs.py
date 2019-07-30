import requests,json,re
import copy
from random import random
from tabulate import tabulate

# Constants:
startelo = 0
ignoreMapType = False
stageDecayFactor = 0.8
k = 32
d = 200
loops = 100000
teams = ['ATL','BOS','CDH','DAL','FLA','GZC','HZS','HOU','LDN','GLA','VAL','NYE','PAR','PHI','SFS','SEO','SHD','TOR','VAN','WAS']
pteams = ["NYE","VAN","HZS","SFS","SEO","VAL","HOU","SHD"]

r=requests.get("https://api.overwatchleague.com/schedule?expand=team.content&locale=en_US&season=2019",timeout=10).text
rawdata = json.loads(r)
stages = rawdata["data"]["stages"]

maprecord = []
completed = []

for i in [0,1,3,4]:
    stage = stages[i]["matches"]

    for j in range(0,len(stage)):
        match = stage[j]
        if not match["state"]=="CONCLUDED": continue

        p1 = match["competitors"][0]["abbreviatedName"]
        p2 = match["competitors"][1]["abbreviatedName"]

        if i==3 and j>=70:
            completed.append([p1,p2,match["wins"][0]>match["wins"][1]])

        for game in match["games"]:
            score1=0.5+(0.5 if game["points"][0]>game["points"][1] else 0)-(0.5 if game["points"][1]>game["points"][0] else 0)
            score2=0.5-(0.5 if game["points"][0]>game["points"][1] else 0)+(0.5 if game["points"][1]>game["points"][0] else 0)

            maptype = ""
            if i==0:
                maptype = {1:'control',2:'hybrid',3:'assault',4:'escort',5:'control',6:'hybrid',7:'escort'}[game["number"]]
            elif j<70:
                maptype = {1:'control',2:'assault',3:'hybrid',4:'escort',5:'control'}[game["number"]]
            else:
                maptype = {1:'control',2:'hybrid',3:'assault',4:'escort',5:'control',6:'hybrid',7:'escort'}[game["number"]]

            maprecord.append([maptype,p1,p2,score1,score2,i,j])

teamelos = {
    'assault': {t:startelo for t in teams},
    'control': {t:startelo for t in teams},
    'escort':  {t:startelo for t in teams},
    'hybrid':  {t:startelo for t in teams}
}

overallteamelos = {t:startelo for t in teams}
print(completed)

for m in maprecord:
    mtype = m[0]
    p1,p2 = m[1],m[2]
    as1,as2 = m[3],m[4] # actual scores

    if m[6]==0:
        for t in teams: overallteamelos[t]*=stageDecayFactor
        for m in teamelos:
            for t in teams: teamelos[m][t]*=stageDecayFactor

    # map based

    elo1,elo2 = teamelos[mtype][p1],teamelos[mtype][p2]

    es1 = 1/(1+10**((elo2-elo1)/d)) # expected scores
    es2 = 1/(1+10**((elo1-elo2)/d))

    teamelos[mtype][p1] += k*(as1-es1)
    teamelos[mtype][p2] += k*(as2-es2)

    # total

    elo1,elo2 = overallteamelos[p1],overallteamelos[p2]

    es1 = 1/(1+10**((elo2-elo1)/d)) # expected scores
    es2 = 1/(1+10**((elo1-elo2)/d))

    overallteamelos[p1] += k*(as1-es1)
    overallteamelos[p2] += k*(as2-es2)

def simulatePlayoffs(pteams):
    def simulateMatch(t1,t2,firstto):
        if any([(t1 in c and t2 in c) for c in completed]):
            completedmatch = next(c for c in completed if (t1 in c and t2 in c))
            return (completedmatch[2]) == (completedmatch[0]==t1)
        
        maporder = ['control','hybrid','assault','escort','control','hybrid','escort']
        wins = [0,0]
        for m in maporder:
            elo1,elo2 = teamelos[m][t1],teamelos[m][t2]
            p = 1/(1+10**((elo2-elo1)/d))
            if random()<p: wins[0]+=1
            else: wins[1]+=1
            if max(wins)>=firstto: break
        return wins[0]>wins[1]
    
    def fight(category,t1,t2,rounds):
        return category[t1] if simulateMatch(category[t1],category[t2],rounds) else category[t2]

    semis = []
    semis.append(fight(pteams,0,7,3))
    semis.append(fight(pteams,1,6,3))
    semis.append(fight(pteams,2,5,3))
    semis.append(fight(pteams,3,4,3))
    semis.sort(key=lambda x:pteams.index(x))

    finals = []
    finals.append(fight(semis,0,3,4))
    finals.append(fight(semis,1,2,4))
    finals.sort(key=lambda x:pteams.index(x))

    winner = []
    winner.append(fight(finals,0,1,4))

    placements = [winner[0]]
    placements.append([t for t in finals if t not in winner][0])
    placements.extend([t for t in semis if t not in finals])
    placements.extend([t for t in pteams if t not in semis])

    return placements


playoffplacements = {t:[0,0,0,0] for t in teams}
avgearnings = {t:0 for t in teams}

rewards = [200000,100000,50000,50000,25000,25000,25000,25000]

for x in range(loops):
    results = simulatePlayoffs(pteams)

    for t in pteams:
        pl = results.index(t)+1
        if pl<=1: playoffplacements[t][0]+=1
        if pl<=2: playoffplacements[t][1]+=1
        if pl<=4: playoffplacements[t][2]+=1
        playoffplacements[t][3]+=1

        avgearnings[t]+=rewards[pl-1]

table = [["Team","Top 1","Top 2","Top 4","Top 8","Earnings"]]
for t in sorted(pteams,key=lambda x:(playoffplacements[x][0],avgearnings[x]),reverse=True):
    table.append([t]+["{:.2%}".format(playoffplacements[t][i]/loops) for i in range(4)]+["${:,.2f}".format(avgearnings[t]/loops)])

print(tabulate(table))
