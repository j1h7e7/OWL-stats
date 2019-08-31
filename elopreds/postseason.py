from elocalculations import EloCalculations, teams
from tabulate import tabulate
import copy

atl_div = ['ATL','BOS','FLA','HOU','LDN','NYE','PAR','PHI','TOR','WAS']
pac_div = ['CDH','DAL','GZC','HZS','GLA','VAL','SFS','SEO','SHD','VAN']

top6  = {t:0 for t in teams}
top12 = {t:0 for t in teams}
avg_place = {t:0 for t in teams}

teamplayoffs = {t:[0,0,0,0,0,0,0,0,0] for t in teams}

placement_rate = {t:[0]*20 for t in teams}

playoffteamlist = {}

loops = 10000

baseseason = EloCalculations()
baseseason.calculateElos()
season = EloCalculations()

for i in range(loops):
    season.makeCopy(baseseason)

    finalstandings = sorted(teams,key=lambda t:(season.standings[t]['w'],season.standings[t]['d']),reverse=True)

    for t in teams:
        if finalstandings.index(t)<6: top6[t]+=1
        if finalstandings.index(t)<12: top12[t]+=1
        avg_place[t]+=finalstandings.index(t)+1

        placement_rate[t][finalstandings.index(t)]+=1

    # POSTSEASON
    atl_lead = sorted(atl_div,key=finalstandings.index)[0]
    pac_lead = sorted(pac_div,key=finalstandings.index)[0]

    playoffteams = [atl_lead,pac_lead]
    playoffteams.sort(key=finalstandings.index)
    playoffteams.extend([t for t in finalstandings if t not in playoffteams][0:4])
    playinteams = [t for t in finalstandings if t not in playoffteams][0:6]

    playinsemi1 = season.simulateSingleMatch(playinteams[2],playinteams[5],[],type='playoffs')
    playinsemi2 = season.simulateSingleMatch(playinteams[3],playinteams[4],[],type='playoffs')
    playinsemiwins = sorted([playinsemi1[0],playinsemi2[0]],key=playinteams.index)

    playinfinal1 = season.simulateSingleMatch(playinteams[1],playinsemiwins[0],[],type='playoffs')
    playinfinal2 = season.simulateSingleMatch(playinteams[0],playinsemiwins[1],[],type='playoffs')
    playinwilds = sorted([playinfinal1[0],playinfinal2[0]],key=playinteams.index)
    playoffteams.extend(playinwilds)

    match1 = season.simulateSingleMatch(playoffteams[0],playoffteams[7],[],type='playoffs')
    match2 = season.simulateSingleMatch(playoffteams[3],playoffteams[4],[],type='playoffs')
    match3 = season.simulateSingleMatch(playoffteams[1],playoffteams[6],[],type='playoffs')
    match4 = season.simulateSingleMatch(playoffteams[2],playoffteams[5],[],type='playoffs')

    match5 = sorted([match1[1],match2[1]],key=playoffteams.index)
    match6 = sorted([match3[1],match4[1]],key=playoffteams.index)
    match5 = season.simulateSingleMatch(match5[0],match5[1],[],type='playoffs')
    match6 = season.simulateSingleMatch(match6[0],match6[1],[],type='playoffs')

    match7 = sorted([match1[0],match2[0]],key=playoffteams.index)
    match8 = sorted([match3[0],match4[0]],key=playoffteams.index)
    match7 = season.simulateSingleMatch(match7[0],match7[1],[],type='playoffs')
    match8 = season.simulateSingleMatch(match8[0],match8[1],[],type='playoffs')

    match9  = sorted([match8[1],match5[0]],key=playoffteams.index)
    match10 = sorted([match7[1],match6[0]],key=playoffteams.index)
    match9  = season.simulateSingleMatch(match9[0],match9[1],[],type='playoffs')
    match10 = season.simulateSingleMatch(match10[0],match10[1],[],type='playoffs')

    match12 = sorted([match7[0],match8[0]],key=playoffteams.index)
    match12 = season.simulateSingleMatch(match12[0],match12[1],[],type='playoffs')

    match11 = sorted([match9[0],match10[0]],key=playoffteams.index)
    match11 = season.simulateSingleMatch(match11[0],match11[1],[],type='playoffs')

    match13 = sorted([match12[1],match11[0]],key=playoffteams.index)
    match13 = season.simulateSingleMatch(match13[0],match13[1],[],type='playoffs')

    grandfinals = sorted([match13[0],match12[0]],key=playoffteams.index)
    grandfinals = season.simulateSingleMatch(grandfinals[0],grandfinals[1],[],type='playoffs')

    winner = [grandfinals[0]]

    playoffplacements = [grandfinals[0]]            # 1st place
    playoffplacements.append(grandfinals[1])        # 2nd place
    playoffplacements.append(match13[1])            # 3rd place
    playoffplacements.append(match11[1])            # 4th place
    playoffplacements.extend([match9[1],match10[1]])# 5-6th place
    playoffplacements.extend([match5[1],match6[1]]) # 7-8th place

    playoffplacements.extend([playinfinal1[1],playinfinal2[1]]) # 9-10th place
    playoffplacements.extend([playinsemi1[1],playinsemi2[1]]) # 11-12th place

    playoffplacements.extend(finalstandings[12:20])

    '''print("Play-ins  ",playinteams)
    print("Play-in r1",playinsemi1,playinsemi2)
    print("Play-in r2",playinfinal1,playinfinal2)
    print("Playoffs  ",playoffteams)
    print("Quarters  ",match1,match2,match3,match4)
    print("L Semis 1 ",match5,match6)
    print("W Semis   ",match7,match8)
    print("L Semis 2 ",match9,match10)
    print("W Finals  ",match12)
    print("L Finals 1",match11)
    print("L Finals 2",match13)
    print("Grnd Final",grandfinals)
    print("Winner    ",winner)

    print(playoffplacements)'''

    for t in teams:
        if playoffplacements.index(t)<1: teamplayoffs[t][0]+=1
        if playoffplacements.index(t)<2: teamplayoffs[t][1]+=1
        if playoffplacements.index(t)<3: teamplayoffs[t][2]+=1
        if playoffplacements.index(t)<4: teamplayoffs[t][3]+=1
        if playoffplacements.index(t)<6: teamplayoffs[t][4]+=1
        if playoffplacements.index(t)<8: teamplayoffs[t][5]+=1
        if playoffplacements.index(t)<10: teamplayoffs[t][6]+=1
        if playoffplacements.index(t)<12: teamplayoffs[t][7]+=1
        teamplayoffs[t][8]+=1
    
    pt = ''.join(playoffteams)
    if pt not in playoffteamlist: playoffteamlist[pt]=0
    playoffteamlist[pt]+=1

    if i%int(loops/100)==0: print(int(100*i/loops))

table1 = [['Team','Top 6','Top 12','Avg Place']]

for t in sorted(teams,key=lambda x:avg_place[x],reverse=False):
    table1.append([t,"{:.2%}".format(top6[t]/loops),"{:.2%}".format(top12[t]/loops),"{:.2f}".format(avg_place[t]/loops)])

table2 = [['Team','1st','2nd','3rd','4th','5-6th','7-8th','9-10th','11-12th','13-20th']]

for t in sorted(teams,key=lambda t:teamplayoffs[t][0],reverse=True):
    row = [t]
    for i in range(9): row.append("{:.2%}".format(teamplayoffs[t][i]/loops))
    table2.append(row)

def formatzeropercent(x):
    if round(x*100)==0 and x>0: return "<1%"
    elif x==0: return ""
    else: return "{:.0%}".format(x)

table3 = [['Team','1st','2nd','3rd','4th','5th','6th','7th','8th','9th','10th','11th','12th','13th','14th','15th','16th','17th','18th','19th','20th']]

for t in sorted(teams,key=lambda x:avg_place[x],reverse=False):
    table3.append([t]+[formatzeropercent(x/loops) for x in placement_rate[t]])

#print(tabulate(table1))
print(tabulate(table2))
print(tabulate(table3))

likelylist1 = max(playoffteamlist,key=playoffteamlist.get)
likelylist2 = [likelylist1[3*i:3*i+3] for i in range(8)]

print("Most Likely Playoff Team List (w/ seeds):",likelylist2)
print("Which occurred {:.2%} of the time.".format(playoffteamlist[likelylist1]/loops))