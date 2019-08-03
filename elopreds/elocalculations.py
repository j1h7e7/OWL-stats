import json, requests, math, random
#import datagatherer

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

colorrequests = requests.get("https://api.overwatchleague.com/teams",timeout=10).text
colordata = json.loads(colorrequests)['competitors']

class EloCalculations:
    def __init__(self):
        self.teamcolors = {}
        for teamdata in colordata:
            c = teamdata['competitor']
            self.teamcolors[c['abbreviatedName']]=["#"+c['primaryColor'],"#"+c['secondaryColor']]

        self.matchdata = json.loads(open("data.json",'r').read())

        self.overall_elos = {t:start_elo for t in teams}
        self.maptype_elos = {t:{m:start_elo for m in maptypes} for t in teams}
        self.mapname_elos = {t:{m:start_elo for m in mapnames} for t in teams}

        self.elorecords = {t:[[],[],[],[]] for t in teams}
        self.stage4played = {t:0 for t in teams}
        self.map_draws = {m:[0,0] for m in mapnames}

        self.standings = {t:{'w':0,'l':0,'d':0} for t in teams}

        self.margins_of_victory = []

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
            for t in teams: self.elorecords[t][i].append(self.overall_elos[t])

            for match in stage['regular']+stage['playoffs']:
                if not match['completed']: continue

                t1, t2 = match['t1'], match['t2']

                if i==3:
                    self.stage4played[t1]+=1
                    self.stage4played[t2]+=1

                # Season Standing W/L
                if match in stage['regular']:
                    if len([x for x in match['maps'] if x['result']=='t1'])>len([x for x in match['maps'] if x['result']=='t2']):
                        self.standings[t1]['w']+=1
                        self.standings[t2]['l']+=1
                    else:
                        self.standings[t1]['l']+=1
                        self.standings[t2]['w']+=1

                for map in match['maps']:
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

                    if match in stage['regular']:
                        self.standings[t1]['d']+= 1 if map['result']=='t1' else -1 if map['result']=='t2' else 0      # Standings Differential
                        self.standings[t2]['d']+= 1 if map['result']=='t2' else -1 if map['result']=='t1' else 0

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

                    self.margins_of_victory.append(MoV)
                    
                    mult = math.log(1 + MoV) * 1 / (elo_dif * 0.001 + 1)

                    t1_change = k * (act_t1 - exp_t1) * mult
                    t2_change = k * (act_t2 - exp_t2) * mult

                    self.overall_elos[t1] += t1_change
                    self.maptype_elos[t1][map["maptype"]] += t1_change
                    self.mapname_elos[t1][map["mapname"]] += t1_change

                    self.overall_elos[t2] += t2_change
                    self.maptype_elos[t2][map["maptype"]] += t2_change
                    self.mapname_elos[t2][map["mapname"]] += t2_change

                    self.elorecords[t1][i].append(self.overall_elos[t1])
                    self.elorecords[t2][i].append(self.overall_elos[t2])

    def getMapType(self,name):
        types = {
            **dict.fromkeys(['hanamura','horizon-lunar-colony','temple-of-anubis','volskaya','paris'],'assault'),
            **dict.fromkeys(['dorado','junkertown','rialto','route-66','gibraltar','Havana'],'escort'),
            **dict.fromkeys(['blizzard-world','eichenwalde','hollywood','kings-row','numbani'],'hybrid'),
            **dict.fromkeys(['busan','ilios','lijiang','nepal','oasis'],'control')
        }

        return types[name]
    
    def predictMatch(self,team1, team2, maps, loops = 10000):
        results = {}
        team1wins = 0
        maptypes = list(map(self.getMapType,maps))

        for x in range(loops):
            team1score = 0
            team2score = 0

            for i in range(len(maps)):
                drawchance = self.map_draws[maps[i]][0]/self.map_draws[maps[i]][1]

                elo1 = (self.overall_elos[team1]*overall_weight + 
                        self.mapname_elos[team1][maps[i]]*mapname_weight + 
                        self.maptype_elos[team1][maptypes[i]]*maptype_weight)
                elo2 = (self.overall_elos[team2]*overall_weight + 
                        self.mapname_elos[team2][maps[i]]*mapname_weight + 
                        self.maptype_elos[team2][maptypes[i]]*maptype_weight)
                
                random_roll = random.random()
                team1winchance = 1/(1+10**((elo2-elo1)/d))

                #drawchance *= min(team1winchance,1-team1winchance)*2

                if random_roll < team1winchance - drawchance/2: team1score +=1
                elif random_roll < team1winchance + drawchance/2: pass
                else: team2score +=1
            
            if team1score==team2score:
                map5 = random.choice([m for m in ['ilios','busan','lijiang'] if m not in maps])

                elo1 = (self.overall_elos[team1]*overall_weight +
                        self.maptype_elos[team1]['control']*maptype_weight +
                        self.mapname_elos[team1][map5]*mapname_weight)
                elo2 = (self.overall_elos[team2]*overall_weight +
                        self.maptype_elos[team2]['control']*maptype_weight +
                        self.mapname_elos[team2][map5]*mapname_weight)

                if random.random()< 1/(1+10**((elo2-elo1)/d)): team1score+=1
                else: team2score +=1
            
            scoreline = "{}-{}".format(team1score,team2score)
            if scoreline not in results: results[scoreline]=0
            results[scoreline]+=1
            if team1score>team2score: team1wins += 1 

        
        results = {s:results[s]/loops for s in results}
        return results, team1wins/loops

    def simulateSingleMatch(self, team1, team2, maps, type='regular', updateelos=True, firstto=4):
        '''
        Type can be regular, or playoffs.
        It is assumed team1 is the higher seed.
        '''

        types = [self.getMapType(m) for m in maps]

        score = [0,0]

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
                MoV = random.choice(self.margins_of_victory)

                exp_t1 = 1/(1+10**((elo2-elo1)/d))      # Expected Scores
                exp_t2 = 1/(1+10**((elo1-elo2)/d))

                if act_t1==1:   elo_dif = elo1-elo2
                elif act_t2==1: elo_dif = elo2-elo1
                else:
                    if elo1>elo2:   elo_dif = elo1-elo2
                    elif elo1>elo2: elo_dif = elo2-elo1
                    else:           elo_dif = 0

                mult = math.log(1 + MoV) * 1 / (elo_dif * 0.001 + 1)
                t1_change = k * (act_t1 - exp_t1) * mult
                t2_change = k * (act_t2 - exp_t2) * mult
                
                self.overall_elos[team1] += t1_change
                self.maptype_elos[team1][maptype] += t1_change
                self.mapname_elos[team1][mapname] += t1_change

                self.overall_elos[team2] += t2_change
                self.maptype_elos[team2][maptype] += t2_change
                self.mapname_elos[team2][mapname] += t2_change

            return round(act_t1),round(act_t2)
        
        if type=='regular':
            for i in range(len(maps)):
                score1,score2 = simulateMap(maps[i],types[i])
                score[0]+=score1
                score[1]+=score2
        
            if score[0]==score[1]:
                map5 = random.choice([x for x in mapnames if self.getMapType(x)=='control' and x not in maps])
                score1,score2 = simulateMap(map5,'control')
                score[0]+=score1
                score[1]+=score2
            
            if score[0]>score[1]:
                self.standings[team1]['w']+=1
                self.standings[team2]['l']+=1
            else:
                self.standings[team1]['l']+=1
                self.standings[team2]['w']+=1
            
            self.standings[team1]['d']+=score[0]-score[1]
            self.standings[team2]['d']+=score[1]-score[0]

        if type=='playoffs':
            mappreferences = {t:{mt:[x for x in mapnames if self.getMapType(x)==mt] for mt in maptypes} for t in [team1,team2]}
            for t in [team1,team2]:
                for mt in maptypes:
                    mappreferences[t][mt].sort(key=lambda x:self.mapname_elos[t][x]-self.mapname_elos[{team1:team2,team2:team1}[t]][x],reverse=True)

            mapprogression = ['control','hybrid','assault','escort']

            scores = [0,0]
            mnum = 0
            played = []
            picker = team1

            while max(score)<firstto:
                mtype = mapprogression[mnum%4]
                mname = [m for m in mappreferences[picker][mtype] if m not in played][0]
                played.append(mname)
                mnum += 1

                score1,score2 = simulateMap(mname,mtype)

                if score1==1:
                    picker=team2
                    score[0]+=1
                elif score2==1:
                    picker=team1
                    score[1]+=1

            if score[0]>score[1]: return [team1,team2]
            else: return [team2,team1]

        return
