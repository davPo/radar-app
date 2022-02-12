



var points = [];

function destroyRadarPoints(){
	// Remove each radar point from the map.
	points.forEach(function(element){
		element.remove();
	});
	// Clear the range ring array.
	points = [];
}

// custom icon for radar point
var div_circle = L.divIcon({ className: 'circle', iconSize: 10})

// add all points to the map
// data.positions is array of [lat,lon]
function handleRadarPoints(data) {
    destroyRadarPoints();
    for (var p of data.positions) {
        var echo = L.marker(p, {icon: div_circle})
        .addTo(map);
        points.push(echo);
    }
    

}