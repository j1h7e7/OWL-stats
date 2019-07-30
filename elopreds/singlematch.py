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
mteams = ["WAS","TOR"]
#[["SHD","VAN"],["VAL","SFS"]][0]
#[["HOU","VAN"],["SHD","NYE"],["SEO","SFS"],["VAL","HZS"]][1]
seriesfirstto = 3

r=requests.get("https://api.overwatchleague.com/schedule?expand=team.content&locale=en_US&season=2019",timeout=10).text
rawdata = json.loads(r)
stages = rawdata["data"]["stages"]

maprecord = []

for i in [0,1,3,4]:
    stage = stages[i]["matches"]

    for j in range(0,len(stage)):
        match = stage[j]
        if not match["state"]=="CONCLUDED": continue

        p1 = match["competitors"][0]["abbreviatedName"]
        p2 = match["competitors"][1]["abbreviatedName"]

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

def simulateMatch(t1,t2,firstto):
    maporder = ['control','hybrid','assault','escort','control','hybrid','escort']
    wins = [0,0]
    for m in maporder:
        elo1,elo2 = teamelos[m][t1],teamelos[m][t2]
        p = 1/(1+10**((elo2-elo1)/d))
        if random()<p: wins[0]+=1
        else: wins[1]+=1
        if max(wins)>=firstto: break
    return wins

matchresults = [0]*(seriesfirstto*2)
possibleresults = sorted([x for x in [[i,j] for i in range(seriesfirstto+1) for j in range(seriesfirstto+1)] if max(x)==seriesfirstto and x[0]!=x[1]],key=lambda x:x[1]-x[0])
#[[4,0],[4,1],[4,2],[4,3],[3,4],[2,4],[1,4],[0,4]]

rewards = [200000,100000,50000,50000,25000,25000,25000,25000]

for x in range(loops):
    results = simulateMatch(mteams[0],mteams[1],seriesfirstto)

    for i in range(len(possibleresults)):
        if results==possibleresults[i]: matchresults[i]+=1

table = []
for i in range(len(possibleresults)):
    table.append(["{} {}-{} {}".format(mteams[0],possibleresults[i][0],possibleresults[i][1],mteams[1]),"{:.2%}".format(matchresults[i]/loops)])

print(tabulate(table))
