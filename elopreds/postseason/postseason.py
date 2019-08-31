from elocalculations import EloCalculations
from tabulate import tabulate
import copy, sys
import time

teams = ["VAN","NYE","SFS","HZS","GLA","ATL","LDN","SEO","GZC","PHI","SHD","CDH"]
finalstandings = ["VAN","NYE","SFS","HZS","GLA","ATL","LDN","SEO","GZC","PHI","SHD","CDH"]
playinteams = ["LDN","SEO","GZC","PHI","SHD","CDH"]

teamplayoffs = {t:[0,0,0,0,0,0,0,0] for t in teams}
playoffteamlist = {}

loops = 10000
decay_factor = 0.8

baseseason = EloCalculations()
baseseason.calculateElos()
for t in teams:
    baseseason.overall_elos[t]*=decay_factor
    for m in baseseason.mapname_elos[t]: baseseason.mapname_elos[t][m]*=decay_factor
    for m in baseseason.maptype_elos[t]: baseseason.maptype_elos[t][m]*=decay_factor
season = EloCalculations()
games = ['']*17

starttime = time.time()

for i in range(loops):
    season.makeCopy(baseseason)

    playoffteams = ["VAN","NYE","SFS","HZS","GLA","ATL"]

    # POSTSEASON
    games[0] = season.simulateMatch(playinteams[2],playinteams[5])                   # 9th seed vs 12th seed
    games[1] = season.simulateMatch(playinteams[3],playinteams[4])                   # 10th seed vs 11th seed
    playinsemiwins = sorted([games[0][0],games[1][0]],key=playinteams.index)

    games[2] = season.simulateMatch(playinteams[0],playinsemiwins[1])               # 7th seed vs lower remaining seed
    games[3] = season.simulateMatch(playinteams[1],playinsemiwins[0])               # 8th seed vs higher remaining seed
    playinwilds = sorted([games[2][0],games[3][0]],key=playinteams.index)
    playoffteams.extend(playinwilds)

    games[4] = season.simulateMatch(playoffteams[0],playoffteams[7])      # (1) 1st seed vs 8th seed
    games[5] = season.simulateMatch(playoffteams[3],playoffteams[4])      # (2) 4th seed vs 5th seed

    games[6] = season.simulateMatch(playoffteams[1],playoffteams[6])      # (3) 2nd seed vs 7th seed
    games[7] = season.simulateMatch(playoffteams[2],playoffteams[5])      # (4) 3rd seed vs 6th seed

    games[8] = sorted([games[4][1],games[5][1]],key=playoffteams.index)       # (5) loser of m1 vs loser of m2
    games[8] = season.simulateMatch(games[8][0],games[8][1])
    games[9] = sorted([games[6][1],games[7][1]],key=playoffteams.index)       # (6) loser of m3 vs loser of m4
    games[9] = season.simulateMatch(games[9][0],games[9][1])

    games[10] = sorted([games[4][0],games[5][0]],key=playoffteams.index)       # (7) winner of m1 vs winner of m2
    games[10] = season.simulateMatch(games[10][0],games[10][1])
    games[11] = sorted([games[6][0],games[7][0]],key=playoffteams.index)       # (8) winner of m3 vs winner of m4
    games[11] = season.simulateMatch(games[11][0],games[11][1])

    games[12]  = sorted([games[11][1],games[8][0]],key=playoffteams.index)      # (9) loser of m8 vs winner of m5
    games[12]  = season.simulateMatch(games[12][0],games[12][1])
    games[13] = sorted([games[10][1],games[9][0]],key=playoffteams.index)      # (10) loser of m7 vs winner of m6
    games[13] = season.simulateMatch(games[13][0],games[13][1])

    games[14] = sorted([games[10][0],games[11][0]],key=playoffteams.index)      # (12) winner of m7 vs winner of m8
    games[14] = season.simulateMatch(games[14][0],games[14][1])

    games[15] = sorted([games[12][0],games[13][0]],key=playoffteams.index)     # (11) winner of m9 vs winner of m10
    games[15] = season.simulateMatch(games[15][0],games[15][1])

    games[16] = sorted([games[14][1],games[15][0]],key=playoffteams.index)    # (13) loser of m12 vs winner of m11
    games[16] = season.simulateMatch(games[16][0],games[16][1])

    grandfinals = sorted([games[16][0],games[14][0]],key=playoffteams.index)    # winner of m12 vs winner of m13
    grandfinals = season.simulateMatch(grandfinals[0],grandfinals[1])

    winner = [grandfinals[0]]

    playoffplacements = [grandfinals[0]]            # 1st place
    playoffplacements.append(grandfinals[1])        # 2nd place
    playoffplacements.append(games[16][1])            # 3rd place
    playoffplacements.append(games[15][1])            # 4th place
    playoffplacements.extend([games[12][1],games[13][1]])# 5-6th place
    playoffplacements.extend([games[8][1],games[9][1]]) # 7-8th place

    playoffplacements.extend([games[2][1],games[3][1]]) # 9-10th place
    playoffplacements.extend([games[0][1],games[1][1]]) # 11-12th place

    for t in teams:
        if playoffplacements.index(t)<1: teamplayoffs[t][0]+=1
        if playoffplacements.index(t)<2: teamplayoffs[t][1]+=1
        if playoffplacements.index(t)<3: teamplayoffs[t][2]+=1
        if playoffplacements.index(t)<4: teamplayoffs[t][3]+=1
        if playoffplacements.index(t)<6: teamplayoffs[t][4]+=1
        if playoffplacements.index(t)<8: teamplayoffs[t][5]+=1
        if playoffplacements.index(t)<10: teamplayoffs[t][6]+=1
        if playoffplacements.index(t)<12: teamplayoffs[t][7]+=1
    
    pt = ''.join(playoffteams)
    if pt not in playoffteamlist: playoffteamlist[pt]=0
    playoffteamlist[pt]+=1

    if i%int(loops/100)==0:
        sys.stdout.write('\r')
        sys.stdout.write("{:.0%}".format(i/loops))
        sys.stdout.flush()


table1 = [['Team','1st','2nd','3rd','4th','5-6th','7-8th','9-10th','11-12th','Elo']]

for t in sorted(teams,key=lambda t:teamplayoffs[t][0],reverse=True):
    row = [t]
    for i in range(8): row.append("{:.2%}".format(teamplayoffs[t][i]/loops))
    row.append(int(baseseason.overall_elos[t]))
    table1.append(row)

print()
print(tabulate(table1))

likelylist1 = max(playoffteamlist,key=playoffteamlist.get)
likelylist2 = [likelylist1[3*i:3*i+3] for i in range(8)]

print("Most Likely Playoff Team List:",likelylist2)
print("Which occurred {:.2%} of the time.".format(playoffteamlist[likelylist1]/loops))

#print(time.time()-starttime)
#print(season.timespent)