from pureelo import EloCalculations

season = EloCalculations()

brierscore = [0,0]
outcomescore = [0,0]

for i in range(4):
    stage = season.matchdata['stages'][i]
    season.applyStageDecay()

    for match in stage['regular']:
        pred = season.predictMatch(match)
        if len([x for x in match['maps'] if x['result']=='t1'])>len([x for x in match['maps'] if x['result']=='t2']):
            bscore = (1-pred[0])**2
            if pred[0]>0.5: outcomescore[0]+=1
        else:
            bscore = (0-pred[0])**2
            if pred[1]>0.5: outcomescore[0]+=1
        
        brierscore[0]+=bscore
        brierscore[1]+=1
        outcomescore[1]+=1

        season.eloCalculateMatch(match)

        print("completed {}-{}  {:.3f}".format(match['t1'],match['t2'],bscore))

print("Brier Score: {:.4f}".format(brierscore[0]/brierscore[1]))
print("Brier Skill Score: {:.4%}".format(1-0.25*(brierscore[0]/brierscore[1])))
print("% Correct Prediction: {:.4%}".format(outcomescore[0]/outcomescore[1]))