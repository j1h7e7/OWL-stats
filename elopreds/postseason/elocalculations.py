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

    def makeCopy(self, season):
        self.overall_elos = {t:season.overall_elos[t] for t in teams}
        self.maptype_elos = {t:{m:season.maptype_elos[t][m] for m in maptypes} for t in teams}
        self.mapname_elos = {t:{m:season.mapname_elos[t][m] for m in mapnames} for t in teams}

        self.map_draws = {m:[season.map_draws[m][0],season.map_draws[m][1]] for m in mapnames}
        self.margins_of_victory = [x for x in season.margins_of_victory]

    def calculateElos(self):
        def applyStageDecay():
            for t in teams:
                self.overall_elos[t]*=decay_factor
                for m in mapnames:
                    self.mapname_elos[t][m]*=decay_factor
                for m in maptypes:
                    self.maptype_elos[t][m]*=decay_factor

        for i in range(4):
            stage = self.matchdata['stages'][i]
            applyStageDecay()

            for match in stage['regular']+stage['playoffs']:
                self.eloCalculateMatch(match)

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
    
    def predictMatch(self, team1, team2, loops = 10000):
        wins = [0,0]

        for x in range(loops):
            result = self.simulateMatch(team1,team2,False)
            if result[0]==team1: wins[0]+=1
            elif result[0]==team2: wins[1]+=1
        
        return wins

    def simulateMatch(self, team1, team2, updateelos=True, firstto=4):
        '''
        Type can be regular, or playoffs.
        It is assumed team1 is the higher seed.
        '''

        def simulateMap(mapname,maptype):
            elo1 = (self.overall_elos[team1]*overall_weight + 
                    self.mapname_elos[team1][mapname]*mapname_weight + 
                    self.maptype_elos[team1][maptype]*maptype_weight)
            elo2 = (self.overall_elos[team2]*overall_weight + 
                    self.mapname_elos[team2][mapname]*mapname_weight + 
                    self.maptype_elos[team2][maptype]*maptype_weight)
            
            random_roll = random.random()
            team1winchance = 1/(1+10**((elo2-elo1)/d))
            drawchance = self.map_draws[mapname][0]/self.map_draws[mapname][1] * min(team1winchance,1-team1winchance)*2

            if random_roll < team1winchance - drawchance/2:     act_t1, act_t2 = 1,0
            elif random_roll < team1winchance + drawchance/2:   act_t1, act_t2 = 0.5,0.5
            else:                                               act_t1, act_t2 = 0,1
            
            if updateelos:
                mult = random.choice(self.margins_of_victory)

                exp_t1 = 1/(1+10**((elo2-elo1)/d))      # Expected Scores
                exp_t2 = 1/(1+10**((elo1-elo2)/d))

                if act_t1==1:   elo_dif = elo1-elo2
                elif act_t2==1: elo_dif = elo2-elo1
                else:
                    if elo1>elo2:   elo_dif = elo1-elo2
                    elif elo1>elo2: elo_dif = elo2-elo1
                    else:           elo_dif = 0

                #t1 = time.time()
                t1_change = k * (act_t1 - exp_t1) * mult
                t2_change = k * (act_t2 - exp_t2) * mult
                #self.timespent += time.time()-t1
                
                self.overall_elos[team1] += t1_change
                self.maptype_elos[team1][maptype] += t1_change
                self.mapname_elos[team1][mapname] += t1_change

                self.overall_elos[team2] += t2_change
                self.maptype_elos[team2][maptype] += t2_change
                self.mapname_elos[team2][mapname] += t2_change

            return round(act_t1),round(act_t2)

        mappreferences = {t:{mt:[x for x in postseasonmappool if self.maptypesbymap[x]==mt] for mt in maptypes} for t in [team1,team2]}
        for t in [team1,team2]:
            for mt in maptypes:
                mappreferences[t][mt].sort(key=lambda x:self.mapname_elos[t][x]-self.mapname_elos[{team1:team2,team2:team1}[t]][x],reverse=True)

        mapprogression = ['control','hybrid','assault','escort','control','hybrid','escort','control'] #?????????

        score = [0,0]
        mnum = 0
        picker = team1

        while max(score)<firstto:
            try: mtype = mapprogression[mnum]
            except IndexError:
                if score[1]>score[0]: return [team2,team1]
                else: return [team1,team2]
            mname = mappreferences[picker][mtype][0]
            mnum += 1
            mappreferences[team1][mtype].remove(mname)
            mappreferences[team2][mtype].remove(mname)

            score1,score2 = simulateMap(mname,mtype)

            if score1==1:
                picker=team2
                score[0]+=1
            elif score2==1:
                picker=team1
                score[1]+=1

        if score[0]>score[1]: return [team1,team2]
        else: return [team2,team1]
