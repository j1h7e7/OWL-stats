import json, requests, math
from matplotlib import pyplot as plt,gridspec,lines

# Constants:
start_elo = 0           # Starting elo
decay_factor = 0.9      # Decay % between stages
k = 30                  # k for elo change
d = 200                 # Difference in elo for 75% expected WR

overall_weight = 0.60
maptype_weight = 0.20
mapname_weight = 0.20

# Cosmetic Scaling:
elo_center = 1000
elo_scaler = 1
plt.figure(figsize=(20,7))

colorrequests = requests.get("https://api.overwatchleague.com/teams",timeout=10).text
colordata = json.loads(colorrequests)['competitors']
teamcolors = {}
for teamdata in colordata:
    c = teamdata['competitor']
    teamcolors[c['abbreviatedName']]=["#"+c['primaryColor'],"#"+c['secondaryColor']]

teams = ['ATL','BOS','CDH','DAL','FLA','GZC','HZS','HOU','LDN','GLA','VAL','NYE','PAR','PHI','SFS','SEO','SHD','TOR','VAN','WAS']
maptypes = ['control','assault','hybrid','escort']
mapnames = ['Havana', 'temple-of-anubis', 'kings-row', 'hanamura', 'gibraltar', 'numbani', 'volskaya',
            'hollywood', 'dorado', 'nepal', 'route-66', 'lijiang', 'ilios', 'eichenwalde', 'oasis',
            'horizon-lunar-colony', 'junkertown', 'blizzard-world', 'rialto', 'busan', 'paris']

matchdata = json.loads(open("data.json",'r').read())

overall_elos = {t:start_elo for t in teams}
maptype_elos = {t:{m:start_elo for m in maptypes} for t in teams}
mapname_elos = {t:{m:start_elo for m in mapnames} for t in teams}

elorecords = {t:[[],[],[],[]] for t in teams}
stage4played = {t:0 for t in teams}

def applyStageDecay():
    for t in teams:
        overall_elos[t]*=decay_factor
        for m in mapnames:
            mapname_elos[t][m]*=decay_factor
        for m in maptypes:
            maptype_elos[t][m]*=decay_factor

for i in range(4):
    stage = matchdata['stages'][i]
    applyStageDecay()
    for t in teams: elorecords[t][i].append(overall_elos[t])

    for match in stage['regular']+stage['playoffs']:
        if not match['completed']: continue

        t1, t2 = match['t1'], match['t2']

        if i==3:
            stage4played[t1]+=1
            stage4played[t2]+=1

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

            elorecords[t1][i].append(overall_elos[t1])
            elorecords[t2][i].append(overall_elos[t2])

# Elo Horizontal Lines
for i in range(-10,10):
    plt.axhline(y=i*100*elo_scaler+elo_center,color='black',lw=0.5)

# Elo Trend Lines
width = 1.5
for t in teams:
    for stage in range(3):
        stageelos = elorecords[t][stage]
        x = [stage+i/(len(stageelos)) for i in range(len(stageelos))]
        y = [stageelos[i]*elo_scaler+elo_center for i in range(len(stageelos))]
        plt.plot(x,y,color=teamcolors[t][0],lw=width)
        plt.plot(x,y,color=teamcolors[t][1],linestyle='dashed',dashes=[5,5],lw=width)

    stageelos = elorecords[t][3]
    x = [3+i*stage4played[t]/(7*len(stageelos)) for i in range(min(len(stageelos),28))]
    y = [stageelos[i]*elo_scaler+elo_center for i in range(min(len(stageelos),28))]
    plt.plot(x,y,color=teamcolors[t][0],lw=width)
    plt.plot(x,y,color=teamcolors[t][1],linestyle='dashed',dashes=[3,3],lw=width)

# Stage Division Lines
for i in range(4):
    plt.axvline(x=i,color='black',lw=2)

# Background Shading
for i in range(-20,20,2):
    plt.axhspan(elo_center-25*i*elo_scaler,elo_center-25*(i+1)*elo_scaler,color='#DDDDDD')

# Labels/Axes
plt.annotate("Stage 1",xy=(0.125, -0.05),xycoords='axes fraction',ha='center',size=15)
plt.annotate("Stage 2",xy=(0.375, -0.05),xycoords='axes fraction',ha='center',size=15)
plt.annotate("Stage 3",xy=(0.625, -0.05),xycoords='axes fraction',ha='center',size=15)
plt.annotate("Stage 4",xy=(0.875, -0.05),xycoords='axes fraction',ha='center',size=15)
plt.ylabel("Elo Rating")
plt.xticks([])
plt.yticks(range(elo_center-elo_scaler*500,elo_center+elo_scaler*500,elo_scaler*50))

# Graph Bounds
maxelo = max([max([max(x) for x in elorecords[t]]) for t in teams])
minelo = min([min([min(x) for x in elorecords[t]]) for t in teams])
plt.ylim([elo_center+elo_scaler*1.1*minelo,elo_center+elo_scaler*1.1*maxelo])
plt.xlim([0,4])

# Legend
legend1, legend2 = [], []
for t in teams:
    legend1.append((lines.Line2D([],[],color=teamcolors[t][0],lw=width),lines.Line2D([],[],color=teamcolors[t][1],linestyle='dashed',dashes=[3,3],lw=width)))
    legend2.append(t)
plt.legend(legend1,legend2,bbox_to_anchor=(1.04,1), loc="upper left")

print("Final Elos:")
for t in sorted(teams,key=lambda x:elorecords[x][3][-1],reverse=True):
    print("{}: {}".format(t,int(elo_center+elo_scaler*elorecords[t][3][-1])))

plt.show()
