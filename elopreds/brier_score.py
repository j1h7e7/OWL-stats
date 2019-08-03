import json, requests, math, random
from tabulate import tabulate

teams = ['ATL','BOS','CDH','DAL','FLA','GZC','HZS','HOU','LDN','GLA','VAL','NYE','PAR','PHI','SFS','SEO','SHD','TOR','VAN','WAS']
maptypes = ['control','assault','hybrid','escort']
mapnames = ['Havana', 'temple-of-anubis', 'kings-row', 'hanamura', 'gibraltar', 'numbani', 'volskaya',
            'hollywood', 'dorado', 'nepal', 'route-66', 'lijiang', 'ilios', 'eichenwalde', 'oasis',
            'horizon-lunar-colony', 'junkertown', 'blizzard-world', 'rialto', 'busan', 'paris']

# Constants:
start_elo = 0           # Starting elo
d = 200                 # Difference in elo for 75% expected WR

def applyStageDecay():
    for t in teams:
        overall_elos[t]*=decay_factor
        for m in mapnames:
            mapname_elos[t][m]*=decay_factor
        for m in maptypes:
            maptype_elos[t][m]*=decay_factor

def predictMatch(team1, team2, maps, maptypes):
    global overall_elos, maptype_elos, mapname_elos
    team1wins = 0
    loops = 100

    for x in range(loops):
        team1score = 0
        team2score = 0

        for i in range(len(maps)):
            elo1 = (overall_elos[team1]*overall_weight + 
                    mapname_elos[team1][maps[i]]*mapname_weight + 
                    maptype_elos[team1][maptypes[i]]*maptype_weight)
            elo2 = (overall_elos[team2]*overall_weight + 
                    mapname_elos[team2][maps[i]]*mapname_weight + 
                    maptype_elos[team2][maptypes[i]]*maptype_weight)

            if random.random()< 1/(1+10**((elo2-elo1)/d)): team1score+=1
            else: team2score +=1
        
        if team1score==team2score:
            elo1 = (overall_elos[team1]*overall_weight +
                    maptype_elos[team1]['control']*(maptype_weight+mapname_weight))
            elo2 = (overall_elos[team2]*overall_weight +
                    maptype_elos[team2]['control']*(maptype_weight+mapname_weight))

            if random.random()< 1/(1+10**((elo2-elo1)/d)): team1score+=1
            else: team2score +=1

        if team1score>team2score: team1wins+=1

    return team1wins/loops


def testConstants(squared=False):
    global overall_elos, maptype_elos, mapname_elos
    overall_elos = {t:start_elo for t in teams}
    maptype_elos = {t:{m:start_elo for m in maptypes} for t in teams}
    mapname_elos = {t:{m:start_elo for m in mapnames} for t in teams}

    global k, decay_factor, overall_weight, maptype_weight, mapname_weight

    score = [0,0]

    for stage in matchdata['stages']:
        applyStageDecay()

        for match in stage['regular']+stage['playoffs']:
            if not match['completed']: continue

            t1, t2 = match['t1'], match['t2']

            if match in stage['regular']:
                m_maps = [x['mapname'] for x in match['maps']][:4]
                m_types = [x['maptype'] for x in match['maps']][:4]
                result = 1 if len([x for x in match['maps'] if x['result']=='t1'])>len([x for x in match['maps'] if x['result']=='t2']) else 0
                pred = predictMatch(t1,t2,m_maps,m_types)
                dif = abs(result-pred)
                score[0] += dif**2 if squared else dif
                score[1] += 1

            for map in match['maps']:
                t1_elo = (overall_elos[t1]*overall_weight + 
                        mapname_elos[t1][map['mapname']]*mapname_weight + 
                        maptype_elos[t1][map['maptype']]*maptype_weight)
                t2_elo = (overall_elos[t2]*overall_weight + 
                        mapname_elos[t2][map['mapname']]*mapname_weight + 
                        maptype_elos[t2][map['maptype']]*maptype_weight)

                exp_t1 = 1/(1+10**((t2_elo-t1_elo)/d))      # Expected Scores
                exp_t2 = 1/(1+10**((t1_elo-t2_elo)/d))

                act_t1 = 1 if map['result']=='t1' else 0 if map['result']=='t2' else 0.5    # Actual Scores
                act_t2 = 1 if map['result']=='t2' else 0 if map['result']=='t1' else 0.5

                MoV = 1         # Margin of Victory
                elo_dif = 0     # Elo Difference
                if act_t1==1:   # The team that won determines the margin of victory
                    MoV = (map['deaths'][t2]+1)/(map['deaths'][t1]+1)
                    elo_dif = t1_elo-t2_elo
                elif act_t2==1:
                    MoV = (map['deaths'][t1]+1)/(map['deaths'][t2]+1)
                    elo_dif = t2_elo-t1_elo
                else:           # In case of a draw, the team with higher elo determines margin of "victory"
                    if t1_elo>t2_elo:
                        MoV = (map['deaths'][t2]+1)/(map['deaths'][t1]+1)
                        elo_dif = t1_elo-t2_elo
                    elif t1_elo>t2_elo:
                        MoV = (map['deaths'][t1]+1)/(map['deaths'][t2]+1)
                        elo_dif = t2_elo-t1_elo
                
                mult = math.log(1 + MoV) * 1 / (elo_dif * 0.001 + 1)

                t1_change = k * (act_t1 - exp_t1) * mult
                t2_change = k * (act_t2 - exp_t2) * mult

                overall_elos[t1] += t1_change
                maptype_elos[t1][map["maptype"]] += t1_change
                mapname_elos[t1][map["mapname"]] += t1_change

                overall_elos[t2] += t2_change
                maptype_elos[t2][map["maptype"]] += t2_change
                mapname_elos[t2][map["mapname"]] += t2_change

    return score[0]/score[1]

########################################################################################
########################################################################################
########################################################################################
########################################################################################

matchdata = json.loads(open("data.json",'r').read())

overall_elos = {t:start_elo for t in teams}
maptype_elos = {t:{m:start_elo for m in maptypes} for t in teams}
mapname_elos = {t:{m:start_elo for m in mapnames} for t in teams}


scores = {}

decay_factor = 0.9
k = 50

overall_weight = 0.60
maptype_weight = 0.20
mapname_weight = 0.20

'''for x1 in range(1,20):
    maptype_weight = x1/20
    scores[x1] = {}

    for x2 in range(1,20-x1):
        mapnamee_weight = x2/20
        overall_weight = 1-mapname_weight-maptype_weight

        scores[x1][x2] = testConstants()

    print(x1)#'''

for x1 in range(2,20):
    decay_factor = x1/20
    scores[x1] = {}

    for x2 in range(20,70,2):
        k = x2
        scores[x1][x2] = testConstants()

    print(x1)#'''

#print(testConstants(squared=False))

print(scores)
