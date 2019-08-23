// Get stored match/map data
var stageData = JSON.parse(stageRecord)['stages'];

var mapList = [];

for (i=0;i<4;i++) {
    var stage = stageData[i];
    var regular = stage['regular'];
    var playoffs = stage['playoffs'];

    for (j=0;j<regular.length;j++) {
        var match = regular[j];
        if (!match['completed']) continue;
        var t1 = match['t1'];
        var t2 = match['t2'];
        var maps = match['maps']
        var week = match['week']

        for (k=0;k<maps.length;k++){
            var mapstat = maps[k];
            mapstat['t1']=t1;
            mapstat['t2']=t2;
            mapstat['stage']=i+1;
            mapstat['week']=week+1;
            mapstat['matchNumber']=j+1;
            mapstat['type']='regular';
            mapList.push(mapstat);
        }
    }

    for (j=0;j<playoffs.length;j++) {
        var match = playoffs[j];
        if (!match['completed']) continue;
        var t1 = match['t1'];
        var t2 = match['t2'];
        var maps = match['maps']

        for (k=0;k<maps.length;k++){
            var mapstat = maps[k];
            mapstat['t1']=t1;
            mapstat['t2']=t2;
            mapstat['stage']=i+1;
            mapstat['matchNumber']=j+1;
            mapstat['type']='playoffs';
            mapList.push(mapstat);
        }
    }
}