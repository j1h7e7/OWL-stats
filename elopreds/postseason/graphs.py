from elocalculations import EloCalculations
from matplotlib import pyplot as plt,gridspec,lines
import json

teams = ["VAN","NYE","SFS","HZS","GLA","ATL","LDN","SEO","GZC","PHI","SHD","CDH"]
decay_factor = 0.8

season = EloCalculations()
season.calculateElos()
for t in teams:
    season.overall_elos[t]*=decay_factor
    for m in season.mapname_elos[t]: season.mapname_elos[t][m]*=decay_factor
    for m in season.maptype_elos[t]: season.maptype_elos[t][m]*=decay_factor

postseasondata = json.loads(open("data.json").read())

# Cosmetic Scaling:
elo_center = 1000
elo_scaler = 1
plt.figure(figsize=(20,7))

# Elo Horizontal Lines
for i in range(-10,10):
    plt.axhline(y=i*100*elo_scaler+elo_center,color='black',lw=0.5)

teamx = {t:[] for t in teams}
teamy = {t:[season.overall_elos[t]] for t in teams}
for t in teams:
    if teams.index(t)>7: teamx[t].append(0)
    elif teams.index(t)>5: teamx[t].append(1)
    else: teamx[t].append(2)

matchconstants = [0,0,1,1,2,2,2,2,3,3,3,3,4,4,4,5,6,7]
numrounds = 6  # Number of sepearated rounds (such as semis, losers R2, etc.)

for i in range(17):
    match = postseasondata[i]
    if match['maps']:
        t1, t2 = match['t1'], match['t2']
        for team in [t1,t2]:
            teamy[team].append(season.overall_elos[team])
            teamx[team].append(matchconstants[i])
        
        for m in range(len(match['maps'])):
            map = match['maps'][m]
            season.eloCalculateMap(map,t1,t2)
            for team in [t1,t2]:
                teamy[team].append(season.overall_elos[team])
                teamx[team].append(matchconstants[i]+(m+1)/len(match['maps']))

# Elo Trend Lines
width = 1.5
for t in teams:
    x = teamx[t]
    y = [i*elo_scaler+elo_center for i in teamy[t]]
    plt.plot(x,y,color=season.teamcolors[t][0],lw=width)
    plt.plot(x,y,color=season.teamcolors[t][1],linestyle='dashed',dashes=[3,3],lw=width)

# Stage Division Lines
for i in range(numrounds):
    plt.axvline(x=i,color='black',lw=2)

# Background Shading
for i in range(-20,20,2):
    plt.axhspan(elo_center-25*i*elo_scaler,elo_center-25*(i+1)*elo_scaler,color='#DDDDDD')

# Labels/Axes
textsize = 13
plt.annotate("Play-in Quarters",            xy=(1/(2*numrounds), -0.05),xycoords='axes fraction',ha='center',size=textsize,va='center')
plt.annotate("Play-in Semis",               xy=(3/(2*numrounds), -0.05),xycoords='axes fraction',ha='center',size=textsize,va='center')
plt.annotate("Quarterfinals",               xy=(5/(2*numrounds), -0.05),xycoords='axes fraction',ha='center',size=textsize,va='center')
plt.annotate("Semifinals &\nLosers R1",     xy=(7/(2*numrounds), -0.05),xycoords='axes fraction',ha='center',size=textsize,va='center')
plt.annotate("Winners Finals &\nLosers R2", xy=(9/(2*numrounds), -0.05),xycoords='axes fraction',ha='center',size=textsize,va='center')
plt.annotate("Losers R3",                   xy=(11/(2*numrounds), -0.05),xycoords='axes fraction',ha='center',size=textsize,va='center')
plt.ylabel("Elo Rating")
plt.xticks([])
plt.yticks(range(elo_center-elo_scaler*500,elo_center+elo_scaler*500,elo_scaler*50))

'''# Graph Bounds
maxelo = max([max([max(x) for x in season.elorecords[t]]) for t in teams])
minelo = min([min([min(x) for x in season.elorecords[t]]) for t in teams])'''
plt.ylim([900,1200])
plt.xlim([0,numrounds])

# Legend
legend1, legend2 = [], []
for t in teams:
    line1=lines.Line2D([],[],color=season.teamcolors[t][0],lw=width)
    line2=lines.Line2D([],[],color=season.teamcolors[t][1],linestyle='dashed',dashes=[3,3],lw=width)
    legend1.append((line1,line2))
    legend2.append(t)
plt.legend(legend1,legend2,bbox_to_anchor=(1.04,1), loc="upper left")

plt.show()
