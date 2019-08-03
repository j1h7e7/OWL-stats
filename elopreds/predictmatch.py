import sys, re
from elocalculations import EloCalculations

elo_calculator = EloCalculations()

t1 = sys.argv[1]
t2 = sys.argv[2]

maps = sys.argv[3]
maps = re.split("[,\[\]]",maps)[1:5]

prediction, winchance = elo_calculator.predictMatch(t1,t2,maps,loops=1000000)

print("Chance that {} wins: {:.2%}".format(t1,winchance))
print("Chance that {} wins: {:.2%}".format(t2,1-winchance))
print("Individual Outcome Chances:")
for s in sorted([x for x in prediction],key=lambda x: prediction[x],reverse=True):
    print("{} {} {} - {:.2%}".format(t1,s,t2,prediction[s]))