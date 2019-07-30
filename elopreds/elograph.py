import requests,json,re
import copy
from matplotlib import pyplot as plt,gridspec,lines

# Constants:
startelo = 0
ignoreMapType = False
stageDecayFactor = 0.8
k = 32
d = 200
loops = 10000
teams = ['ATL','BOS','CDH','DAL','FLA','GZC','HZS','HOU','LDN','GLA','VAL','NYE','PAR','PHI','SFS','SEO','SHD','TOR','VAN','WAS']

# Cosmetic Scaling:
elo_center = 1000
elo_scaler = 10

plt.figure(figsize=(20,7))

colorrequests = requests.get("https://api.overwatchleague.com/teams",timeout=10).text
colordata = json.loads(colorrequests)['competitors']
teamcolors = {}
for teamdata in colordata:
    c = teamdata['competitor']
    teamcolors[c['abbreviatedName']]=["#"+c['primaryColor'],"#"+c['secondaryColor']]

r=requests.get("https://api.overwatchleague.com/schedule?expand=team.content&locale=en_US&season=2019",timeout=10).text
rawdata = json.loads(r)
stages = rawdata["data"]["stages"]

maprecord = []

for i in [0,1,3,4]:
    stage = stages[i]["matches"]

    for j in range(0,len(stage)):
        match = stage[j]
        if len(match["games"])==0 and j>=70: continue

        p1 = match["competitors"][0]["abbreviatedName"]
        p2 = match["competitors"][1]["abbreviatedName"]
        
        if match["state"]!="CONCLUDED": continue
        if len(match["games"])==0: continue

        realstage = [0,1,'',2,3][i]

        for k in range(len(match["games"])):
            game = match["games"][k]
            score1=0.5+(0.5 if game["points"][0]>game["points"][1] else 0)-(0.5 if game["points"][1]>game["points"][0] else 0)
            score2=0.5-(0.5 if game["points"][0]>game["points"][1] else 0)+(0.5 if game["points"][1]>game["points"][0] else 0)

            maprecord.append({'p1':p1,'p2':p2,'score1':score1,'score2':score2,'stage':realstage,'match':j,'game':k})

print("Data scraping done")
print("Most recent match: {} vs {}".format(maprecord[-1]['p1'],maprecord[-1]['p2']))

teamelos = {t:startelo for t in teams}
elorecords = {t:[[startelo],[],[],[]] for t in teams}
stage4played = {t:0 for t in teams}

for m in maprecord:
    p1,p2 = m['p1'],m['p2']             # players
    as1,as2 = m['score1'],m['score2']   # actual scores

    if m['match']==0 and m['game']==0 and m['stage']>0:         # elo decay if first game of stage
        for t in teams:
            teamelos[t]*=stageDecayFactor
            elorecords[t][m['stage']].append(teamelos[t])

    if m['stage']==3 and m['game']==0:
        stage4played[p1]+=1
        stage4played[p2]+=1

    elo1,elo2 = teamelos[p1],teamelos[p2]

    es1 = 1/(1+10**((elo2-elo1)/d)) # expected scores
    es2 = 1/(1+10**((elo1-elo2)/d))

    teamelos[p1] += k*(as1-es1)
    teamelos[p2] += k*(as2-es2)

    elorecords[p1][m['stage']].append(teamelos[p1])
    elorecords[p2][m['stage']].append(teamelos[p2])

print("Final Elos:")
for t in sorted(teams,key=lambda x:elorecords[x][3][-1],reverse=True):
    print("{}: {}".format(t,int(elo_center+elo_scaler*elorecords[t][3][-1])))

# Elo Horizontal Lines
for i in range(-10,10):
    plt.axhline(y=i*20*elo_scaler+elo_center,color='black',lw=0.5)

# Elo Trend Lines
width = 2
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
    plt.axhspan(elo_center-5*i*elo_scaler,elo_center-5*(i+1)*elo_scaler,color='#DDDDDD')

# Labels/Axes
plt.annotate("Stage 1",xy=(0.125, -0.05),xycoords='axes fraction',ha='center',size=15)
plt.annotate("Stage 2",xy=(0.375, -0.05),xycoords='axes fraction',ha='center',size=15)
plt.annotate("Stage 3",xy=(0.625, -0.05),xycoords='axes fraction',ha='center',size=15)
plt.annotate("Stage 4",xy=(0.875, -0.05),xycoords='axes fraction',ha='center',size=15)
plt.ylabel("Elo Rating")
plt.xticks([])
plt.yticks(range(elo_center-elo_scaler*100,elo_center+elo_scaler*100,elo_scaler*10))

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

plt.show()
