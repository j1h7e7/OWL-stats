import json, requests, math
#import datagatherer

# Constants:
start_elo = 0           # Starting elo
decay_factor = 0.9      # Decay % between stages
k = 30                  # k for elo change
d = 200                 # Difference in elo for 75% expected WR

overall_weight = 0.60
maptype_weight = 0.20
mapname_weight = 0.20

teams = ['ATL','BOS','CDH','DAL','FLA','GZC','HZS','HOU','LDN','GLA','VAL','NYE','PAR','PHI','SFS','SEO','SHD','TOR','VAN','WAS']
maptypes = ['control','assault','hybrid','escort']
mapnames = ['Havana', 'temple-of-anubis', 'kings-row', 'hanamura', 'gibraltar', 'numbani', 'volskaya',
            'hollywood', 'dorado', 'nepal', 'route-66', 'lijiang', 'ilios', 'eichenwalde', 'oasis',
            'horizon-lunar-colony', 'junkertown', 'blizzard-world', 'rialto', 'busan', 'paris']

matchdata = json.loads(open("data.json",'r').read())

overall_elos = {t:start_elo for t in teams}
maptype_elos = {t:{m:start_elo for m in maptypes} for t in teams}
mapname_elos = {t:{m:start_elo for m in mapnames} for t in teams}

map_draws = {m:[0,0] for m in mapnames}

def applyStageDecay():
    for t in teams:
        overall_elos[t]*=decay_factor
        for m in mapnames:
            mapname_elos[t][m]*=decay_factor
        for m in maptypes:
            maptype_elos[t][m]*=decay_factor

for stage in matchdata['stages']:
    applyStageDecay()

    for match in stage['regular']+stage['playoffs']:
        if not match['completed']: continue

        t1, t2 = match['t1'], match['t2']

        for game in match['maps']:
            t1_elo = (overall_elos[t1]*overall_weight + 
                      mapname_elos[t1][game['mapname']]*mapname_weight + 
                      maptype_elos[t1][game['maptype']]*maptype_weight)
            t2_elo = (overall_elos[t2]*overall_weight + 
                     mapname_elos[t2][game['mapname']]*mapname_weight + 
                     maptype_elos[t2][game['maptype']]*maptype_weight)

            exp_t1 = 1/(1+10**((t2_elo-t1_elo)/d))      # Expected Scores
            exp_t2 = 1/(1+10**((t1_elo-t2_elo)/d))

            act_t1 = 1 if game['result']=='t1' else 0 if game['result']=='t2' else 0.5    # Actual Scores
            act_t2 = 1 if game['result']=='t2' else 0 if game['result']=='t1' else 0.5

            map_draws[game['mapname']][1]+=1        # Draw %
            if act_t1==0.5: map_draws[game['mapname']][0]+=1

            MoV = 1         # Margin of Victory
            elo_dif = 0     # Elo Difference
            if act_t1==1:   # The team that won determines the margin of victory
                MoV = (game['deaths'][t2]+1)/(game['deaths'][t1]+1)
                elo_dif = t1_elo-t2_elo
            elif act_t2==1:
                MoV = (game['deaths'][t1]+1)/(game['deaths'][t2]+1)
                elo_dif = t2_elo-t1_elo
            else:           # In case of a draw, the team with higher elo determines margin of "victory"
                if t1_elo>t2_elo:
                    MoV = (game['deaths'][t2]+1)/(game['deaths'][t1]+1)
                    elo_dif = t1_elo-t2_elo
                elif t1_elo>t2_elo:
                    MoV = (game['deaths'][t1]+1)/(game['deaths'][t2]+1)
                    elo_dif = t2_elo-t1_elo
            
            mult = math.log(1 + MoV) * 1 / (elo_dif * 0.001 + 1)

            t1_change = k * (act_t1 - exp_t1) * mult
            t2_change = k * (act_t2 - exp_t2) * mult

            overall_elos[t1] += t1_change
            maptype_elos[t1][game["maptype"]] += t1_change
            mapname_elos[t1][game["mapname"]] += t1_change

            overall_elos[t2] += t2_change
            maptype_elos[t2][game["maptype"]] += t2_change
            mapname_elos[t2][game["mapname"]] += t2_change
