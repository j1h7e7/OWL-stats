// Get team data
var http = new XMLHttpRequest();
http.open("GET","https://api.overwatchleague.com/teams?expand=team.content&locale=en-us",false);
http.send(null);
var rawTeams = JSON.parse(http.responseText)['competitors'];
var teams = {}
var teamNames = []
for (var i=0;i<rawTeams.length;i++) {
    var id = rawTeams[i]['competitor']['id'];
    var name = rawTeams[i]['competitor']['abbreviatedName'];
    var fullName = rawTeams[i]['competitor']['name']
    var logo = rawTeams[i]['competitor']['logo'];
    var color = rawTeams[i]['competitor']['primaryColor'];
    teams[name]={'id':id,'logo':logo,'color':color,'fullname':fullName};
    teamNames.push(name)
}

// Get id from name
function IDFromName(name) {
    for (let team of teams) {
        if (team.name==name) {
            return team.id;
        }
    }
}