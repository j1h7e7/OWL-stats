import json, requests

skipcompletedmatches = True

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
    'cache-control': 'private, max-age=0, no-cache'
}

mapguids = {}
mapguiddata = json.loads(requests.get("https://api.overwatchleague.com/maps",timeout=10).text)
for m in mapguiddata:
    mapguids[m["guid"]]=m["id"]

teamids = {}
teamiddata = json.loads(requests.get("https://api.overwatchleague.com/teams",timeout=10).text)
for t in teamiddata['competitors']:
    teamids[t['competitor']['id']] = t['competitor']['abbreviatedName']

schedule = json.loads(requests.get("https://api.overwatchleague.com/schedule?season=2019&separateStagePlayoffsWeek=true",timeout=10).text)
playoffs = schedule["data"]["stages"][5]['weeks']

finaldata = []
if skipcompletedmatches:
    try: finaldata = json.loads(open("data.json",'r').read())
    except FileNotFoundError: pass

#print(playoffs)

matchnumber = -1

for w in range(4):
    week = playoffs[w]["matches"]

    for j in range(0,len(week)):
        matchnumber += 1
        if skipcompletedmatches:
            if finaldata[matchnumber]['completed']: continue

        match = week[j]
        matchid = match['id']

        if match['state']=='PENDING':
            try: matchdata = {'completed':False,'maps':[],'t1':match["competitors"][0]["abbreviatedName"],'t2':match["competitors"][1]["abbreviatedName"]}
            except TypeError: matchdata = {'completed':False,'maps':[]}
            print("Skipping {}-{} because not completed".format(w,j))
        elif match['state']=='IN_PROGRESS':
            p1 = match["competitors"][0]["abbreviatedName"]
            p2 = match["competitors"][1]["abbreviatedName"]
            matchdata = {'completed':False,'maps':[],'t1':p1,'t2':p2}

            for game in match["games"]:
                if game['state']!='CONCLUDED':
                    print("{} vs {}, {}-{}-{} Still Pending".format(p1,p2,w,j,game["number"]))
                    continue

                mapname = mapguids[game['attributes']['mapGuid']]
                maptype = {1:'control',2:'hybrid',3:'assault',4:'escort',5:'control',6:'hybrid',7:'escort',8:'control'}[game["number"]]

                result = 't1' if game['points'][0]>game['points'][1] else 't2' if game['points'][1]>game['points'][0] else 'draw'

                try:
                    url = "https://api.overwatchleague.com/stats/matches/{}/maps/{}".format(matchid,game["number"])
                    maprawdata = json.loads(requests.get(url,headers=headers).text)
                except json.decoder.JSONDecodeError:
                    matchdata['maps'].append({'maptype':maptype,'mapname':mapname,'result':result,'deaths':{p1:0,p2:0}})
                    print("DECODE ERROR AT: {} vs {}, {}-{}-{}".format(p1,p2,w,j,game["number"]))
                    continue

                deaths = {}
                try: deaths[teamids[maprawdata['teams'][0]['esports_team_id']]] = maprawdata['teams'][0]['stats'][0]['value']
                except IndexError: deaths[teamids[maprawdata['teams'][0]['esports_team_id']]] = 0
                try: deaths[teamids[maprawdata['teams'][1]['esports_team_id']]] = maprawdata['teams'][1]['stats'][0]['value']
                except IndexError: deaths[teamids[maprawdata['teams'][1]['esports_team_id']]] = 0

                matchdata['maps'].append({'maptype':maptype,'mapname':mapname,'result':result,'deaths':deaths})
                print("{} vs {}, {}-{}-{}".format(p1,p2,w,j,game["number"]))
            print("Partially Completed {} vs {}, {}-{}".format(p1,p2,w,j))
        else:
            p1 = match["competitors"][0]["abbreviatedName"]
            p2 = match["competitors"][1]["abbreviatedName"]
            matchdata = {'completed':True,'maps':[],'t1':p1,'t2':p2}

            for game in match["games"]:
                mapname = mapguids[game['attributes']['mapGuid']]
                maptype = {1:'control',2:'hybrid',3:'assault',4:'escort',5:'control',6:'hybrid',7:'escort',8:'control'}[game["number"]]

                result = 't1' if game['points'][0]>game['points'][1] else 't2' if game['points'][1]>game['points'][0] else 'draw'

                try:
                    url = "https://api.overwatchleague.com/stats/matches/{}/maps/{}".format(matchid,game["number"])
                    maprawdata = json.loads(requests.get(url,headers=headers).text)
                except json.decoder.JSONDecodeError:
                    matchdata['maps'].append({'maptype':maptype,'mapname':mapname,'result':result,'deaths':{p1:0,p2:0}})
                    print("DECODE ERROR AT: {} vs {}, {}-{}-{}".format(p1,p2,w,j,game["number"]))
                    matchdata['completed']=False
                    continue

                if len(maprawdata['teams'])<2:
                    print("Incomplete teams: {} vs {}, {}-{}-{}".format(p1,p2,w,j,game["number"]))
                    continue

                deaths = {}
                try: deaths[teamids[maprawdata['teams'][0]['esports_team_id']]] = maprawdata['teams'][0]['stats'][0]['value']
                except IndexError: deaths[teamids[maprawdata['teams'][0]['esports_team_id']]] = 0
                try: deaths[teamids[maprawdata['teams'][1]['esports_team_id']]] = maprawdata['teams'][1]['stats'][0]['value']
                except IndexError: deaths[teamids[maprawdata['teams'][1]['esports_team_id']]] = 0

                matchdata['maps'].append({'maptype':maptype,'mapname':mapname,'result':result,'deaths':deaths})
                print("{} vs {}, {}-{}-{}".format(p1,p2,w,j,game["number"]))

        if skipcompletedmatches: finaldata[matchnumber]=matchdata
        else: finaldata.append(matchdata)


open('data.json','w').write(json.dumps(finaldata))
print(len(finaldata))
print("Data Updated")
