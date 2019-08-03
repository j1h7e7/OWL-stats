import math
from matplotlib import pyplot as plt,gridspec,lines
from elocalculations import EloCalculations, teams

rankings = EloCalculations()

# Cosmetic Scaling:
elo_center = 1000
elo_scaler = 1
plt.figure(figsize=(20,7))

# Elo Horizontal Lines
for i in range(-10,10):
    plt.axhline(y=i*100*elo_scaler+elo_center,color='black',lw=0.5)

# Elo Trend Lines
width = 1.5
for t in teams:
    for stage in range(3):
        stageelos = rankings.elorecords[t][stage]
        x = [stage+i/(len(stageelos)) for i in range(len(stageelos))]
        y = [stageelos[i]*elo_scaler+elo_center for i in range(len(stageelos))]
        plt.plot(x,y,color=rankings.teamcolors[t][0],lw=width)
        plt.plot(x,y,color=rankings.teamcolors[t][1],linestyle='dashed',dashes=[5,5],lw=width)

    stageelos = rankings.elorecords[t][3]
    x = [3+i*rankings.stage4played[t]/(7*len(stageelos)) for i in range(min(len(stageelos),28))]
    y = [stageelos[i]*elo_scaler+elo_center for i in range(min(len(stageelos),28))]
    plt.plot(x,y,color=rankings.teamcolors[t][0],lw=width)
    plt.plot(x,y,color=rankings.teamcolors[t][1],linestyle='dashed',dashes=[3,3],lw=width)

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
maxelo = max([max([max(x) for x in rankings.elorecords[t]]) for t in teams])
minelo = min([min([min(x) for x in rankings.elorecords[t]]) for t in teams])
plt.ylim([elo_center+elo_scaler*1.1*minelo,elo_center+elo_scaler*1.1*maxelo])
plt.xlim([0,4])

# Legend
legend1, legend2 = [], []
for t in teams:
    line1=lines.Line2D([],[],color=rankings.teamcolors[t][0],lw=width)
    line2=lines.Line2D([],[],color=rankings.teamcolors[t][1],linestyle='dashed',dashes=[3,3],lw=width)
    legend1.append((line1,line2))
    legend2.append(t)
plt.legend(legend1,legend2,bbox_to_anchor=(1.04,1), loc="upper left")

print("Final Elos:")
for t in sorted(teams,key=lambda x:rankings.elorecords[x][3][-1],reverse=True):
    print("{}: {}".format(t,int(elo_center+elo_scaler*rankings.elorecords[t][3][-1])))

plt.show()
