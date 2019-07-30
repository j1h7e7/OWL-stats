import json, requests
import matplotlib.pyplot as plt

matchdata = json.loads(open("data.json",'r').read())

metricdata = []

for i in range(4):
    stage = matchdata['stages'][i]

    regular = stage['regular']
    playoffs = stage['playoffs']

    for match in regular:
        if not match['completed']: continue
        
        for map in match['maps']:
            try:
                t1deaths = map['deaths'][match['t1']]
                t2deaths = map['deaths'][match['t2']]
            except KeyError: print(map,match)

            if map['result']=='t1': metric = (t2deaths+1)/(t1deaths+1)
            elif map['result']=='t2': metric = (t1deaths+1)/(t2deaths+1)
                
            if metric<0.3: print(match['t1'],match['t2'],map['mapname'])

            metricdata.append(metric)

print(metricdata)

plt.hist([x for x in metricdata if x<5],bins=50)

for i in range(10):
    plt.axvline(x=i,color='black',lw=0.5)
plt.show()

print(len([x for x in metricdata if x>=1])/len(metricdata))