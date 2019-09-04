from elocalculations import EloCalculations
from tabulate import tabulate
import copy, sys, json
import time

teams = ["VAN","NYE","SFS","HZS","GLA","ATL","LDN","SEO","GZC","PHI","SHD","CDH"]
finalstandings = ["VAN","NYE","SFS","HZS","GLA","ATL","LDN","SEO","GZC","PHI","SHD","CDH"]
playinteams = ["LDN","SEO","GZC","PHI","SHD","CDH"]

loops = 20000
decay_factor = 0.8

season = EloCalculations()
season.calculateElos()
for t in teams:
    season.overall_elos[t]*=decay_factor
    for m in season.mapname_elos[t]: season.mapname_elos[t][m]*=decay_factor
    for m in season.maptype_elos[t]: season.maptype_elos[t][m]*=decay_factor

postseasondata = json.loads(open("data.json").read())
basegames = ['']*17
for i in range(17):
    match = postseasondata[i]
    if match['maps']:
        season.eloCalculateMatch(match)
        winner = match['t1'] if len([x for x in match['maps'] if x['result']=='t1'])>len([x for x in match['maps'] if x['result']=='t2']) else match['t2']
        loser  = match['t1'] if len([x for x in match['maps'] if x['result']=='t1'])<len([x for x in match['maps'] if x['result']=='t2']) else match['t2']
        basegames[i] = [winner,loser]

    else:
        if 't1' not in match: continue
        pred = season.predictMatch(match['t1'],match['t2'],loops)
        winner = match['t1'] if pred[0]>pred[1] else match['t2']
        print("{} {:.2%} - {:.2%} {}\t\tWinner: {}".format(match['t1'],pred[0]/loops,pred[1]/loops,match['t2'],winner))
