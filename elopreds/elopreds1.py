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
loops = 10000
teams = ['ATL','BOS','CDH','DAL','FLA','GZC','HZS','HOU','LDN','GLA','VAL','NYE','PAR','PHI','SFS','SEO','SHD','TOR','VAN','WAS']

def getMapType(name):
    types = {
        **dict.fromkeys(['hanamura','horizon-lunar-colony','temple-of-anubis','volskaya','paris'],'assault'),
        **dict.fromkeys(['dorado','junkertown','rialto','route-66','gibraltar'],'escort'),
        **dict.fromkeys(['blizzard-world','eichenwalde','hollywood','kings-row','numbani'],'hybrid'),
        **dict.fromkeys(['busan','ilios','lijiang','nepal','oasis'],'control')
    }

    try: return types[name]
    except KeyError:
        print(name)
        return name

r=requests.get("https://api.overwatchleague.com/schedule?expand=team.content&locale=en_US&season=2019",timeout=10).text
rawdata = json.loads(r)
stages = rawdata["data"]["stages"]

maprecord = []
teamrecords = {t:{'w':0,'l':0,'d':0} for t in teams}
tobeplayed = []

for i in [0,1,3,4]:
    stage = stages[i]["matches"]

    for j in range(0,len(stage)):
        match = stage[j]
        if len(match["games"])==0 and j>=70: continue

        p1 = match["competitors"][0]["abbreviatedName"]
        p2 = match["competitors"][1]["abbreviatedName"]

        if j<70:
            if match["state"]=="CONCLUDED":
                if match['wins'][0]>match['wins'][1]:
                    teamrecords[p1]['w']+=1
                    teamrecords[p2]['l']+=1
                else:
                    teamrecords[p1]['l']+=1
                    teamrecords[p2]['w']+=1
                teamrecords[p1]['d']+=match['wins'][0]-match['wins'][1]
                teamrecords[p2]['d']+=match['wins'][1]-match['wins'][0]
            else:
                tobeplayed.append([p1,p2])

        
        if match["state"]!="CONCLUDED": continue
        if len(match["games"])==0: continue

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

print("Data scraping done")
print("Most recent match: {} vs {}".format(maprecord[-1][1],maprecord[-1][2]))

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

'''print(teamelos)
print(overallteamelos)
print(teamrecords)
print(tobeplayed)'''

def simulateSeason(useOverall=False):
    record = copy.deepcopy(teamrecords)
    maporder = ['control','assault','hybrid','escort']

    for match in tobeplayed:
        wins = [0,0]
        for m in maporder:
            elo1,elo2 = teamelos[m][match[0]],teamelos[m][match[1]]
            p = 1/(1+10**((elo2-elo1)/d))
            if random()<p: wins[0]+=1
            else: wins[1]+=1
        if wins[0]==wins[1]:
            elo1,elo2 = teamelos['control'][match[0]],teamelos['control'][match[1]]
            p = 1/(1+10**((elo2-elo1)/d))
            if random()<p: wins[0]+=1
            else: wins[1]+=1

        if wins[0]>wins[1]:
            record[match[0]]['w']+=1
            record[match[1]]['l']+=1
        else:
            record[match[0]]['l']+=1
            record[match[1]]['w']+=1
        record[match[0]]['d']+=wins[0]-wins[1]
        record[match[1]]['d']+=wins[1]-wins[0]

    finalrecord = [record[t]['w']-record[t]['l']+(record[t]['d']/100) for t in teams]

    return [t for _,t in sorted(zip(finalrecord,teams),reverse=True)]

def simulateMatch(t1,t2,firstto):
    maporder = ['control','hybrid','assault','escort','control','hybrid','escort']
    wins = [0,0]
    for m in maporder:
        elo1,elo2 = teamelos[m][t1],teamelos[m][t2]
        p = 1/(1+10**((elo2-elo1)/d))
        if random()<p: wins[0]+=1
        else: wins[1]+=1
        if max(wins)>=firstto: break
    return wins[0]>wins[1]

def simulatePostSeason(season,useOverall=False):
    def fight(category,t1,t2,rounds):
        return category[t1] if simulateMatch(category[t1],category[t2],rounds) else category[t2]

    def rfight(category,rounds):
        return fight(category,0,1,rounds)


    playinsemis = [season[6],season[7]]
    playinsemis.append(fight(season,9,10,4))
    playinsemis.append(fight(season,8,11,4))
    playinsemis.sort(key=lambda x:season.index(x))

    playinwilds = []
    playinwilds.append(fight(playinsemis,0,3,4))
    playinwilds.append(fight(playinsemis,1,2,4))
    playinwilds.sort(key=lambda x:season.index(x))

    playoffteams = []
    playoffteams.extend(season[0:6])
    playoffteams.extend(playinwilds)

    round1 = [playoffteams[0],playoffteams[7]]
    round2 = [playoffteams[3],playoffteams[4]]
    round3 = [playoffteams[1],playoffteams[6]]
    round4 = [playoffteams[2],playoffteams[5]]

    round7 = [rfight(round1,4),rfight(round2,4)]
    round8 = [rfight(round3,4),rfight(round4,4)]

    round5 = [[t for t in round1 if not t in round7][0],[t for t in round2 if not t in round7][0]]
    round6 = [[t for t in round3 if not t in round8][0],[t for t in round4 if not t in round8][0]]

    round12 = [rfight(round7,4),rfight(round8,4)]

    round9  = [[t for t in round8 if not t in round12][0],rfight(round5,4)]
    round10 = [[t for t in round7 if not t in round12][0],rfight(round6,4)]

    round11 = [rfight(round9,4),rfight(round10,4)]

    grandfinals = []
    grandfinals.append(rfight(round12,4))

    round13 = [[t for t in round12 if not t in grandfinals][0],rfight(round11,4)]

    grandfinals.append(rfight(round13,4))

    winner = [fight(grandfinals,0,1,4)]

    placing = [winner[0],[t for t in grandfinals if t not in winner][0]] # 1st and 2nd
    placing.append([t for t in round13 if t not in grandfinals][0])  # 3rd
    placing.append([t for t in round11 if t not in round13][0])
    placing.extend([t for t in round9+round10 if t not in round11])
    placing.extend([t for t in round5+round6 if t not in round9+round10])
    placing.extend([t for t in playinsemis if t not in playinwilds])
    placing.extend([t for t in season[6:12] if t not in playinsemis])
    placing.extend(season[12:])

    '''print(placing)

    print("Play-in:  ",season[6:12])
    print("Semis:    ",playinsemis)
    print("Winners:  ",playinwilds)
    print("Playoffs: ",playoffteams)
    print("W Semis:  ",round7+round8)
    print("L Round 1:",round5+round6)
    print("W Finals: ",round12)
    print("L Round 2:",round9+round10)
    print("L Round 3:",round11)
    print("L Finals: ",round13)
    print("FINALS:   ",grandfinals)
    print("WINNER:   ",winner)'''

    #return winner[0]
    return placing


placements = {t:0 for t in teams}
top6s = {t:0 for t in teams}
top12s = {t:0 for t in teams}
playoffplacements = {t:[0,0,0,0,0,0,0,0,0] for t in teams}
avgearnings = {t:0 for t in teams}

playoffprize = [1100000,600000,450000,350000,300000,300000,200000,200000,0,0,0,0,0,0,0,0,0,0,0,0]

# To ignore maptype WR and look only at map WR:
if ignoreMapType: teamelos = {**dict.fromkeys(['assault','control','hybrid','escort'],overallteamelos)}

for x in range(loops):
    season = simulateSeason()
    postseason = simulatePostSeason(season)
    for t in teams:
        placements[t]+=1+season.index(t)
        top6s[t]+=1 if season.index(t)<6 else 0
        top12s[t]+=1 if season.index(t)<12 else 0

    for t in teams:
        pl = postseason.index(t)+1
        if pl<=1: playoffplacements[t][0]+=1
        if pl<=2: playoffplacements[t][1]+=1
        if pl<=3: playoffplacements[t][2]+=1
        if pl<=4: playoffplacements[t][3]+=1
        if pl<=6: playoffplacements[t][4]+=1
        if pl<=8: playoffplacements[t][5]+=1
        if pl<=10: playoffplacements[t][6]+=1
        if pl<=12: playoffplacements[t][7]+=1
        playoffplacements[t][8]+=1
        avgearnings[t]+=playoffprize[pl-1]


table = [["Team","Top 1","Top 2","Top 3","Top 4","Top 6","Top 8","Top 10","Top 12","Top 20","Earnings:"]]
for t in sorted(teams,key=lambda x:avgearnings[x],reverse=True):
    table.append([t]+["{:.2%}".format(playoffplacements[t][i]/loops) for i in range(9)]+["${:,.2f}".format(avgearnings[t]/loops)])

print(tabulate(table))

table2 = [["Team","Top 6","Top 12","Average Placement"]]
for t in sorted(teams,key=lambda x:placements[x],reverse=False):
    table2.append([t,"{:.2%}".format(top6s[t]/loops),"{:.2%}".format(top12s[t]/loops),round(placements[t]/loops,2)])

print(tabulate(table2))



