var currentmapnum = 0

function description(map,type) {
    var text = "";
    text += map["t1"]+' vs '+map["t2"];
    if (type=="map") {
        var mapname = map["mapname"];
        mapname = mapname.replace(/-/g,' ');
        mapname = mapname.replace(/\b\w/g, l=>l.toUpperCase());
        text += " on "+mapname;
    }
    return text;
}

function updateAll() {
    updateCurrentMap();
    updateCurrentMatch();
    updatePreviousMap();
    updateNextMap();
    updatePreviousMatch();
    updateNextMatch();
}

function updateCurrentMatch() {
    var currentmap = mapList[currentmapnum];
    document.getElementById("cm-team1").innerHTML = '<img src="'+teams[currentmap["t1"]]["logo"]+'" height="42" width="42">';
    document.getElementById("cm-team2").innerHTML = '<img src="'+teams[currentmap["t2"]]["logo"]+'" height="42" width="42">';
    document.getElementById("cm-teamnames").innerHTML = teams[currentmap["t1"]]["fullname"]+' vs. '+teams[currentmap["t2"]]["fullname"]
    //document.getElementById("current-match-teams").innerHTML = '<table><tr><td>'+description(currentmap,"match")+'</td></tr></table>';
}

function updateCurrentMap() {
    var currentmap = mapList[currentmapnum];
    document.getElementById("current-map").innerHTML = "Current Map<br>"+description(currentmap,"map");
    if (currentmap["type"]=="playoffs") {
        document.getElementById("cm-time").innerHTML = "Stage "+currentmap["stage"]+" Playoffs<br><br>"
    } else {
        document.getElementById("cm-time").innerHTML = "Stage "+currentmap["stage"]+" Week "+currentmap["week"]+'<br><br>'
    }
}

function updatePreviousMap() {
    var currentmap = mapList[currentmapnum];
    var text = 'No Previous Map';
    if (currentmapnum>0) {
        var prevmap = mapList[currentmapnum-1];
        if (currentmap['t1']==prevmap['t1'] && currentmap['t2']==prevmap['t2']) {
            text = "Previous Map<br>"+description(prevmap,"map");
        }
    }
    document.getElementById("previous-map").innerHTML = text;
}

function updateNextMap() {
    var currentmap = mapList[currentmapnum];
    var text = 'No Next Map';
    if (currentmapnum<mapList.length-1) {
        var nextmap = mapList[currentmapnum+1];
        if (currentmap['t1']==nextmap['t1'] && nextmap['t2']==nextmap['t2']) {
            text = "Next Map<br>"+description(nextmap,"map");
        }
    }
    document.getElementById("next-map").innerHTML = text;
}

function updatePreviousMatch() {
    var currentmap = mapList[currentmapnum];
    var text = 'No Previous Match';
    for (var i=currentmapnum;i>0;i--) {
        if ((mapList[i]["t1"]!=currentmap["t1"]) && (mapList[i]["t2"]!=currentmap["t2"])) {
            text = "Previous Match<br>"+description(mapList[i],"match")
            break
        }
    }
    document.getElementById("previous-match").innerHTML = text;
}

function updateNextMatch() {
    var currentmap = mapList[currentmapnum];
    var text = 'No Next Match';
    for (var i=currentmapnum;i<mapList.length;i++) {
        if (mapList[i]["t1"]!=currentmap["t1"] && mapList[i]["t2"]!=currentmap["t2"]) {
            text = "Next Match<br>"+description(mapList[i],"match")
            break
        }
    }
    document.getElementById("next-match").innerHTML = text;
}

updateAll();

function increment() {
    updateElos(mapList[currentmapnum]);
    currentmapnum++;
    updateAll();
    updateList();
}
function decrement() {
    //currentmapnum--;
    //updateAll();
}