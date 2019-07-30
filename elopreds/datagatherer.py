import json, requests

mapguids = {}
mapguiddata = json.loads(requests.get("https://api.overwatchleague.com/maps",timeout=10).text)
for m in mapguiddata:
    mapguids[m["guid"]]=m["id"]

teamids = {}
teamiddata = json.loads(requests.get("https://api.overwatchleague.com/teams",timeout=10).text)
for t in teamiddata['competitors']:
    teamids[t['competitor']['id']] = t['competitor']['abbreviatedName']

schedule = json.loads(requests.get("https://api.overwatchleague.com/schedule?season=2019",timeout=10).text)
#finaldata = {'stages':[]}
finaldata = json.loads(open("data.json",'r').read())

stages = schedule["data"]["stages"]

for i in [0,1,3,4]:
    stage = stages[i]["matches"]

    stageid = [0,1,'',2,3][i]

    stagedata = finaldata["stages"][stageid]

    for j in range(0,len(stage)):
        match = stage[j]
        if len(match["games"])==0 and j>=70: continue
        if j<70:
            if stagedata['regular'][j]['completed']:
                #matchdata = {'completed':False,'maps':[],'t1':p1,'t2':p2}
                continue
        else:
            if stagedata['playoffs'][j-70]['completed']: continue

        p1 = match["competitors"][0]["abbreviatedName"]
        p2 = match["competitors"][1]["abbreviatedName"]
        matchid = match['id']

        matchdata = {'completed':False,'maps':[],'t1':p1,'t2':p2}

        if match['state']!='CONCLUDED':
            if j<70:
                stagedata['regular'][j] = matchdata
        else:
            matchdata['completed']=True
            for game in match["games"]:
                mapname = mapguids[game['attributes']['mapGuid']]
                maptype = ""
                if i==0:
                    maptype = {1:'control',2:'hybrid',3:'assault',4:'escort',5:'control',6:'hybrid',7:'escort'}[game["number"]]
                elif j<70:
                    maptype = {1:'control',2:'assault',3:'hybrid',4:'escort',5:'control'}[game["number"]]
                else:
                    maptype = {1:'control',2:'hybrid',3:'assault',0:'escort'}[game["number"]%4]

                result = 't1' if game['points'][0]>game['points'][1] else 't2' if game['points'][1]>game['points'][0] else 'draw'

                try:
                    maprawdata = json.loads(requests.get("https://api.overwatchleague.com/stats/matches/{}/maps/{}".format(matchid,game["number"])).text)
                except json.decoder.JSONDecodeError:
                    matchdata['maps'].append({'maptype':maptype,'mapname':mapname,'result':result,'deaths':{p1:0,p2:0}})
                    print("{}-{}-{}".format(i,j,game["number"]))
                    continue

                deaths = {}
                try: deaths[teamids[maprawdata['teams'][0]['esports_team_id']]] = maprawdata['teams'][0]['stats'][0]['value']
                except IndexError: deaths[teamids[maprawdata['teams'][0]['esports_team_id']]] = 0
                try: deaths[teamids[maprawdata['teams'][1]['esports_team_id']]] = maprawdata['teams'][1]['stats'][0]['value']
                except IndexError: deaths[teamids[maprawdata['teams'][1]['esports_team_id']]] = 0

                matchdata['maps'].append({'maptype':maptype,'mapname':mapname,'result':result,'deaths':deaths})
                print("{}-{}-{}".format(i,j,game["number"]))
        
            if j<70: stagedata['regular'][j] = matchdata
            else: stagedata['playoffs'][j-70] = matchdata

    finaldata['stages'][stageid]

#print(finaldata)

open('data.json','w').write(json.dumps(finaldata))
print("Data Updated")
