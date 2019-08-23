var list = document.getElementById("teamlist");
const start_elo = 0
const k = 30
const d = 200
var elos = {}
for (var tName in teams) elos[tName] = start_elo;

function updateList() {
    teamNames.sort();
    teamNames.sort(function(a,b){return elos[b]-elos[a];});

    var listtext = '';
    for (i=0;i<teamNames.length;i++) {
        listtext += '<li>';
        listtext += '<span class="teamname">'+teams[teamNames[i]]["fullname"]+'</span>';
        listtext += '<span class="teamelo">'+Math.round(elos[teamNames[i]])+'</span>';
        listtext += '<span class="teamrecord">'+'1-1'+'</span>';
        listtext += '<span class="teamdif">'+'+1'+'</span>';
        listtext += '<span class="elodelta">'+'0'+'</span>';
        listtext += '<span class="placedelta">'+'0'+'</span>';
        listtext += '</li>\n';
    }
    list.innerHTML = listtext;
}

function updateElos(map) {
    var t1 = map["t1"];
    var t2 = map["t2"];

    var exp_t1 = 1/(1+10**((elos[t2]-elos[t1])/d));      // Expected Scores
    var exp_t2 = 1/(1+10**((elos[t1]-elos[t2])/d));
    var act_t1 = 0.5;
    var act_t2 = 0.5;

    if (map["result"]=="t1") {
        act_t1 = 1
        act_t2 = 0
    } else if (map["result"]=="t2") {
        act_t1 = 0
        act_t2 = 1
    }

    elos[t1] += k * (act_t1-exp_t1)
    elos[t2] += k * (act_t2-exp_t2)
}

//updateList()