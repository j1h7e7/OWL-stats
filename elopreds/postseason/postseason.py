from elocalculations import EloCalculations
from tabulate import tabulate
import copy, sys, json
import time

teams = ["VAN","NYE","SFS","HZS","GLA","ATL","LDN","SEO","GZC","PHI","SHD","CDH"]
finalstandings = ["VAN","NYE","SFS","HZS","GLA","ATL","LDN","SEO","GZC","PHI","SHD","CDH"]
playinteams = ["LDN","SEO","GZC","PHI","SHD","CDH"]
prizes = [1100000,600000,450000,350000,300000,300000,200000,200000,0,0,0,0]

teamplayoffs = {t:[0,0,0,0,0,0,0,0] for t in teams}
teamprize = {t:0 for t in teams}
likelyteamlist = {}

loops = 10000
decay_factor = 0.8

baseseason = EloCalculations()
baseseason.calculateElos()
for t in teams:
    baseseason.overall_elos[t]*=decay_factor
    for m in baseseason.mapname_elos[t]: baseseason.mapname_elos[t][m]*=decay_factor
    for m in baseseason.maptype_elos[t]: baseseason.maptype_elos[t][m]*=decay_factor
season = EloCalculations()

postseasondata = json.loads(open("data.json").read())
basegames = ['']*17
for i in range(17):
    match = postseasondata[i]
    if match['completed']:
        baseseason.eloCalculateMatch(match)
        winner = match['t1'] if len([x for x in match['maps'] if x['result']=='t1'])>len([x for x in match['maps'] if x['result']=='t2']) else match['t2']
        loser  = match['t1'] if len([x for x in match['maps'] if x['result']=='t1'])<len([x for x in match['maps'] if x['result']=='t2']) else match['t2']
        basegames[i] = [winner,loser]
print([x[0] for x in basegames if x])

starttime = time.time()

for i in range(loops):
    season.makeCopy(baseseason)
    games = copy.deepcopy(basegames)

    playoffteams = ["VAN","NYE","SFS","HZS","GLA","ATL"]

    # POSTSEASON
    games[0] = games[0] or season.simulateMatch(playinteams[2],playinteams[5])      # 9th seed vs 12th seed
    games[1] = games[1] or season.simulateMatch(playinteams[3],playinteams[4])      # 10th seed vs 11th seed
    playinsemiwins = sorted([games[0][0],games[1][0]],key=playinteams.index)

    games[2] = games[2] or season.simulateMatch(playinteams[0],playinsemiwins[1])   # 7th seed vs lower remaining seed
    games[3] = games[3] or season.simulateMatch(playinteams[1],playinsemiwins[0])   # 8th seed vs higher remaining seed
    playinwilds = sorted([games[2][0],games[3][0]],key=playinteams.index)
    playoffteams.extend(playinwilds)

    games[4] = games[4] or season.simulateMatch(playoffteams[0],playoffteams[7])    # (1) 1st seed vs 8th seed      Quarters
    games[5] = games[5] or season.simulateMatch(playoffteams[3],playoffteams[4])    # (2) 4th seed vs 5th seed

    games[6] = games[6] or season.simulateMatch(playoffteams[1],playoffteams[6])    # (3) 2nd seed vs 7th seed      Quarters cont.
    games[7] = games[7] or season.simulateMatch(playoffteams[2],playoffteams[5])    # (4) 3rd seed vs 6th seed

    if not games[8]:
        games[8] = sorted([games[4][1],games[5][1]],key=playoffteams.index)         # (5) loser of m1 vs loser of m2        Losers R1
        games[8] = season.simulateMatch(games[8][0],games[8][1])
    if not games[9]:
        games[9] = sorted([games[6][1],games[7][1]],key=playoffteams.index)         # (6) loser of m3 vs loser of m4        Losers R1
        games[9] = season.simulateMatch(games[9][0],games[9][1])

    if not games[10]:
        games[10] = sorted([games[4][0],games[5][0]],key=playoffteams.index)        # (7) winner of m1 vs winner of m2      Semis
        games[10] = season.simulateMatch(games[10][0],games[10][1])
    if not games[11]:
        games[11] = sorted([games[6][0],games[7][0]],key=playoffteams.index)        # (8) winner of m3 vs winner of m4      Semis
        games[11] = season.simulateMatch(games[11][0],games[11][1])

    if not games[12]:
        games[12]  = sorted([games[11][1],games[8][0]],key=playoffteams.index)      # (9) loser of m8 vs winner of m5       Losers R2
        games[12]  = season.simulateMatch(games[12][0],games[12][1])
    if not games[13]:
        games[13] = sorted([games[10][1],games[9][0]],key=playoffteams.index)       # (10) loser of m7 vs winner of m6      Losers R2
        games[13] = season.simulateMatch(games[13][0],games[13][1])

    if not games[14]:
        games[14] = sorted([games[10][0],games[11][0]],key=playoffteams.index)      # (12) winner of m7 vs winner of m8     Finals
        games[14] = season.simulateMatch(games[14][0],games[14][1])

    if not games[15]:
        games[15] = sorted([games[12][0],games[13][0]],key=playoffteams.index)      # (11) winner of m9 vs winner of m10    Losers R3
        games[15] = season.simulateMatch(games[15][0],games[15][1])

    if not games[16]:
        games[16] = sorted([games[14][1],games[15][0]],key=playoffteams.index)      # (13) loser of m12 vs winner of m11    Losers Finals
        games[16] = season.simulateMatch(games[16][0],games[16][1])

    grandfinals = sorted([games[16][0],games[14][0]],key=playoffteams.index)    # winner of m12 vs winner of m13            Grand Finals
    grandfinals = season.simulateMatch(grandfinals[0],grandfinals[1])

    winner = [grandfinals[0]]

    playoffplacements = [grandfinals[0]]                    # 1st place
    playoffplacements.append(grandfinals[1])                # 2nd place
    playoffplacements.append(games[16][1])                  # 3rd place
    playoffplacements.append(games[15][1])                  # 4th place
    playoffplacements.extend([games[12][1],games[13][1]])   # 5-6th place
    playoffplacements.extend([games[8][1],games[9][1]])     # 7-8th place

    playoffplacements.extend([games[2][1],games[3][1]])     # 9-10th place
    playoffplacements.extend([games[0][1],games[1][1]])     # 11-12th place

    for t in teams:
        if playoffplacements.index(t)<1: teamplayoffs[t][0]+=1
        if playoffplacements.index(t)<2: teamplayoffs[t][1]+=1
        if playoffplacements.index(t)<3: teamplayoffs[t][2]+=1
        if playoffplacements.index(t)<4: teamplayoffs[t][3]+=1
        if playoffplacements.index(t)<6: teamplayoffs[t][4]+=1
        if playoffplacements.index(t)<8: teamplayoffs[t][5]+=1
        if playoffplacements.index(t)<10: teamplayoffs[t][6]+=1
        if playoffplacements.index(t)<12: teamplayoffs[t][7]+=1

        teamprize[t] += prizes[playoffplacements.index(t)]
    
    pt = ''.join([games[x][0] for x in range(len([g for g in basegames if g]),len(games))])
    if pt not in likelyteamlist: likelyteamlist[pt]=0
    likelyteamlist[pt]+=1

    if i%int(loops/100)==0:
        sys.stdout.write('\r')
        sys.stdout.write("{:.0%}".format(i/loops))
        sys.stdout.flush()


table1 = [['Team','1st','2nd','3rd','4th','5-6th','7-8th','9-10th','11-12th','Prize Money','Elo']]
for t in sorted(teams,key=lambda t:(teamplayoffs[t][0],sum(teamplayoffs[t])),reverse=True):
    row = [t]
    for i in range(8): row.append("{:.2%}".format(teamplayoffs[t][i]/loops))
    row.append("${:10,.2f}".format(teamprize[t]/loops))
    row.append(int(baseseason.overall_elos[t]))
    table1.append(row)

table2 = [['Team','1st','2nd','3rd','4th','5-6th','7-8th','Prize Money','Elo']]
for t in sorted([x for x in teams if teamplayoffs[x][5]>0],key=lambda t:(teamplayoffs[t][0],sum(teamplayoffs[t])),reverse=True):
    row = [t]
    for i in range(6): row.append("{:.2%}".format(teamplayoffs[t][i]/loops))
    row.append("${:10,.2f}".format(teamprize[t]/loops))
    row.append(int(baseseason.overall_elos[t]))
    table2.append(row)

print()
print(tabulate(table2))

likelylist1 = max(likelyteamlist,key=likelyteamlist.get)
likelylist2 = [likelylist1[3*i:3*i+3] for i in range(int(len(likelylist1)/3))]

print("Most Likely Bracket Outcome:",likelylist2)
print("Which occurred {:.2%} of the time.".format(likelyteamlist[likelylist1]/loops))

#print(time.time()-starttime)
#print(season.timespent)