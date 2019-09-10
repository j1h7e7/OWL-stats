import json, requests, math, random
import time

# Constants:
start_elo = 0           # Starting elo
decay_factor = 0.9      # Decay % between stages
k = 30                  # k for elo change
d = 200                 # Difference in elo for 75% expected WR
overall_weight = 0.60   # Weigts for different types of elos
maptype_weight = 0.20
mapname_weight = 0.20

teams = ['ATL','BOS','CDH','DAL','FLA','GZC','HZS','HOU','LDN','GLA','VAL','NYE','PAR','PHI','SFS','SEO','SHD','TOR','VAN','WAS']
maptypes = ['control','assault','hybrid','escort']
mapnames = ['Havana', 'temple-of-anubis', 'kings-row', 'hanamura', 'gibraltar', 'numbani', 'volskaya',
                'hollywood', 'dorado', 'nepal', 'route-66', 'lijiang', 'ilios', 'eichenwalde', 'oasis',
                'horizon-lunar-colony', 'junkertown', 'blizzard-world', 'rialto', 'busan', 'paris']

postseasonmappool = ['lijiang','ilios','busan','horizon-lunar-colony','temple-of-anubis','hanamura','numbani','eichenwalde',
                        'kings-row','dorado','gibraltar','rialto']

colorrequests = requests.get("https://api.overwatchleague.com/teams",timeout=10).text
colordata = json.loads(colorrequests)['competitors']

class EloCalculations:
    def __init__(self):
        self.timespent = 0
        self.teamcolors = {}
        for teamdata in colordata:
            c = teamdata['competitor']
            self.teamcolors[c['abbreviatedName']]=["#"+c['primaryColor'],"#"+c['secondaryColor']]

        self.matchdata = json.loads(open("../data.json",'r').read())

        self.overall_elos = {t:start_elo for t in teams}
        self.maptype_elos = {t:{m:start_elo for m in maptypes} for t in teams}
        self.mapname_elos = {t:{m:start_elo for m in mapnames} for t in teams}

        self.map_draws = {m:[0,0] for m in mapnames}
        self.margins_of_victory = []

        self.maptypesbymap = {
            **dict.fromkeys(['hanamura','horizon-lunar-colony','temple-of-anubis','volskaya','paris'],'assault'),
            **dict.fromkeys(['dorado','junkertown','rialto','route-66','gibraltar','Havana'],'escort'),
            **dict.fromkeys(['blizzard-world','eichenwalde','hollywood','kings-row','numbani'],'hybrid'),
            **dict.fromkeys(['busan','ilios','lijiang','nepal','oasis'],'control')
        }

    def calculateElos(self):
        for i in range(4):
            stage = self.matchdata['stages'][i]
            applyStageDecay()

            for match in stage['regular']+stage['playoffs']:
                self.eloCalculateMatch(match)
    
    def applyStageDecay(self):
        for t in teams:
            self.overall_elos[t]*=decay_factor
            for m in mapnames:
                self.mapname_elos[t][m]*=decay_factor
            for m in maptypes:
                self.maptype_elos[t][m]*=decay_factor

    def eloCalculateMatch(self, match):
        t1, t2 = match['t1'], match['t2']

        for map in match['maps']: self.eloCalculateMap(map,t1,t2)

    def eloCalculateMap(self, map, t1, t2):
        t1_elo = (self.overall_elos[t1]*overall_weight + 
                self.mapname_elos[t1][map['mapname']]*mapname_weight + 
                self.maptype_elos[t1][map['maptype']]*maptype_weight)
        t2_elo = (self.overall_elos[t2]*overall_weight + 
                self.mapname_elos[t2][map['mapname']]*mapname_weight + 
                self.maptype_elos[t2][map['maptype']]*maptype_weight)

        exp_t1 = 1/(1+10**((t2_elo-t1_elo)/d))      # Expected Scores
        exp_t2 = 1/(1+10**((t1_elo-t2_elo)/d))

        act_t1 = 1 if map['result']=='t1' else 0 if map['result']=='t2' else 0.5    # Actual Scores
        act_t2 = 1 if map['result']=='t2' else 0 if map['result']=='t1' else 0.5

        self.map_draws[map['mapname']][0] += 1 if act_t1==0.5 else 0    # Draw %
        self.map_draws[map['mapname']][1] += 1

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
        self.margins_of_victory.append(mult)

        t1_change = k * (act_t1 - exp_t1) * mult
        t2_change = k * (act_t2 - exp_t2) * mult

        self.overall_elos[t1] += t1_change
        self.maptype_elos[t1][map["maptype"]] += t1_change
        self.mapname_elos[t1][map["mapname"]] += t1_change

        self.overall_elos[t2] += t2_change
        self.maptype_elos[t2][map["maptype"]] += t2_change
        self.mapname_elos[t2][map["mapname"]] += t2_change
    
    def predictMatch(self, match, loops = 2000):
        wins = [0,0]
        team1,team2 = match['t1'],match['t2']

        for x in range(loops):
            result = self.simulateMatch(team1,team2,match['maps'])
            if result[0]==team1: wins[0]+=1
            elif result[0]==team2: wins[1]+=1

        wins = [x/loops for x in wins]
        
        return wins

    def simulateMatch(self, team1, team2, maps):

        def simulateMap(mapname):
            maptype = self.maptypesbymap[mapname]

            elo1 = (self.overall_elos[team1]*overall_weight + 
                    self.mapname_elos[team1][mapname]*mapname_weight + 
                    self.maptype_elos[team1][maptype]*maptype_weight)
            elo2 = (self.overall_elos[team2]*overall_weight + 
                    self.mapname_elos[team2][mapname]*mapname_weight + 
                    self.maptype_elos[team2][maptype]*maptype_weight)
            
            random_roll = random.random()
            team1winchance = 1/(1+10**((elo2-elo1)/d))
            try: drawchance = self.map_draws[mapname][0]/self.map_draws[mapname][1] * min(team1winchance,1-team1winchance)*2
            except ZeroDivisionError: drawchance = 0

            if random_roll < team1winchance - drawchance/2:     result = [1,0]
            elif random_roll < team1winchance + drawchance/2:   result = [0,0]
            else:                                               result = [0,1]

            return result

        score = [0,0]

        for m in range(4):
            mapresult = simulateMap(maps[m]['mapname'])
            if mapresult[0]==1: score[0]+=1
            if mapresult[1]==1: score[1]+=1

        if score[0]>score[1]: return [team1,team2]
        if score[1]>score[0]: return [team2,team1]

        if len(maps)>4: map5 = maps[4]['mapname']
        else: map5 = random.choice([m for m in mapnames if self.maptypesbymap[m]=='control' and m not in maps])

        mapresult = simulateMap(map5)
        if mapresult[0]==1: return [team1,team2]
        if mapresult[1]==1: return [team2,team1]

        return


if __name__ == "__main__":
    def t1win(match):
        return len([x for x in match['maps'] if x['result']=='t1'])>len([x for x in match['maps'] if x['result']=='t2'])

    season = EloCalculations()

    brierscore = 0
    outcomescore = 0

    allmatches = [match for i in range(4) for match in season.matchdata['stages'][i]['regular']]
    baserate = len([m for m in allmatches if t1win(m)])/len(allmatches)

    for i in range(4):
        stage = season.matchdata['stages'][i]
        season.applyStageDecay()

        for match in stage['regular']:
            pred = season.predictMatch(match)
            if t1win(match):
                bscore = (1-pred[0])**2
                if pred[0]>0.5: outcomescore+=1
            else:
                bscore = (0-pred[0])**2
                if pred[1]>0.5: outcomescore+=1
            
            brierscore+=bscore

            season.eloCalculateMatch(match)

            #print("completed {}-{}  {:.3f}".format(match['t1'],match['t2'],bscore))

    print("k: {}, decay: {}".format(k,decay_factor))
    print("{:.0%} - {:.0%} - {:.0%}".format(overall_weight,maptype_weight,mapname_weight))
    print("% Correct Prediction: {:.2%}".format(outcomescore/280))
    print("Brier Score: {:.4f}".format(brierscore/280))
    print("Brier Skill Score: {:.2%}".format(1-4*(brierscore/280)))