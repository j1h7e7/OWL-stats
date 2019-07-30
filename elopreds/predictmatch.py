import sys, re, random
from elopreds2 import *

t1 = sys.argv[1]
t2 = sys.argv[2]

maps = sys.argv[3]
maps = re.split("[,\[\]]",maps)[1:5]

def getMapType(name):
    types = {
        **dict.fromkeys(['hanamura','horizon-lunar-colony','temple-of-anubis','volskaya','paris'],'assault'),
        **dict.fromkeys(['dorado','junkertown','rialto','route-66','gibraltar','Havana'],'escort'),
        **dict.fromkeys(['blizzard-world','eichenwalde','hollywood','kings-row','numbani'],'hybrid'),
        **dict.fromkeys(['busan','ilios','lijiang','nepal','oasis'],'control')
    }

    return types[name]

def predictMatch(team1, team2, maps):
    results = {}
    team1wins = 0
    loops = 1000000
    maptypes = list(map(getMapType,maps))

    for x in range(loops):
        team1score = 0
        team2score = 0

        for i in range(len(maps)):
            drawchance = map_draws[maps[i]][0]/map_draws[maps[i]][1]

            elo1 = (overall_elos[team1]*overall_weight + 
                    mapname_elos[team1][maps[i]]*mapname_weight + 
                    maptype_elos[team1][maptypes[i]]*maptype_weight)
            elo2 = (overall_elos[team2]*overall_weight + 
                    mapname_elos[team2][maps[i]]*mapname_weight + 
                    maptype_elos[team2][maptypes[i]]*maptype_weight)
            
            random_roll = random.random()
            team1winchance = 1/(1+10**((elo2-elo1)/d))

            drawchance *= min(team1winchance,1-team1winchance)*2

            if random_roll < team1winchance - drawchance/2: team1score +=1
            elif random_roll < team1winchance + drawchance/2: pass
            else: team2score +=1
        
        if team1score==team2score:
            elo1 = (overall_elos[team1]*overall_weight +
                    maptype_elos[team1]['control']*(maptype_weight+mapname_weight))
            elo2 = (overall_elos[team2]*overall_weight +
                    maptype_elos[team2]['control']*(maptype_weight+mapname_weight))

            if random.random()< 1/(1+10**((elo2-elo1)/d)): team1score+=1
            else: team2score +=1
        
        scoreline = "{}-{}".format(team1score,team2score)
        if scoreline not in results: results[scoreline]=0
        results[scoreline]+=1
        if team1score>team2score: team1wins += 1 

    
    results = {s:results[s]/loops for s in results}
    return results, team1wins/loops

prediction, winchance = predictMatch(t1,t2,maps)
print("Chance that {} wins: {:.2%}".format(t1,winchance))
print("Chance that {} wins: {:.2%}".format(t2,1-winchance))
print("Individual Outcome Chances:")
for s in sorted([x for x in prediction],key=lambda x: prediction[x],reverse=True):
    print("{} {} {} - {:.2%}".format(t1,s,t2,prediction[s]))