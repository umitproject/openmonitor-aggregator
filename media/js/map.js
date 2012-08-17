var map;
var mapCluster;
var eventLvl1 = media_url("images/alert1.png");
var eventLvl2 = media_url("images/alert2.png");
var eventLvl3 = media_url("images/alert3.png");
var newevent  = media_url("images/newevent.gif");
var newEventTime = 2000

var MAP_EVENT_URLS = new Array();

function initializeMap()
{
    var latlng = new google.maps.LatLng(0, 0);
    var myOptions = {
        zoom: 3,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);

    var mcOptions = {gridSize: 50, maxZoom: 14};
    mapCluster = new MarkerClusterer(map, [], mcOptions);

    google.maps.event.addListenerOnce(map, 'idle', function(){
       resize_map();
    });
}

function placeNewEvent(type, event, latitude, longitude, alertEvent)
{
    var icon;

    /* get the correct icon */
    switch(type)
    {
        case "Offline":
            icon = eventLvl1
            break
        case "Throttling":
            icon = eventLvl2
            break
        case "Censor":
            icon = eventLvl3
            break
        default:
            icon = eventLvl3
    }

    var marker = new google.maps.Marker({
        position: new google.maps.LatLng(latitude, longitude),
        //title:"Shutdown!",
        icon: icon
    });

    /* set icon animation */
    marker.setAnimation(google.maps.Animation.BOUNCE)

    /* cancel icon animation after newEventTime */
    setInterval(function(){ marker.setAnimation(); }, newEventTime);

    /* create info window */
    var infowindow = new google.maps.InfoWindow({
        content: event
    });

    /* configure click to show info window */
    google.maps.event.addListener(marker, 'click', function() {
        infowindow.open(map, marker);
    });

    mapCluster.addMarker(marker);

    if(alertEvent)
    {
        var alertMarker = new google.maps.Marker({
            position: new google.maps.LatLng(latitude, longitude),
            icon: newevent,
            optimized: false
        });
        
        /* put marker on map */
        alertMarker.setMap(map);

        /* hide event alert after newEventTime */
        setInterval(function(){ alertMarker.setMap(); }, newEventTime);
    }

}

function addEventToMap(event, appear)
{
	var event_summary_div = createEventSummaryDiv(event);
	
    for(i=0; i<event.locations.length; i++)
    {
    	var new_event_summary_div = event_summary_div.clone();
    	
    	var location_name = getFullLocationNameString(event.locations[i]);
    	var extra_info = '<strong>Reported From: </strong>' + location_name;
    	new_event_summary_div.children().filter(".extra").html(extra_info);
    	var event_summary_div_html = "<div style='margin-left:10px'>" +new_event_summary_div.html() + "</div>";
        placeNewEvent(event.type, event_summary_div_html, event.locations[i].lat, event.locations[i].lon, appear)
        //console.info(event.type, event.locations[i].lat, event.locations[i].lon)
    }

    //mapCluster.resetViewport()
    // TODO: format information; show all information
}

function updateInitialMapEvents(m)
{
    events = JSON.parse(m.data);
    for(var i=(events.length-1); i>-1; i--)
    {
        var event = events[i];
        if (MAP_EVENT_URLS.indexOf(event['url']) == -1){
            MAP_EVENT_URLS.push(event['url']);
            addEventToMap(event,false);
        }
        else {
            break;
        }
    }
}

function resize_map(width, height) {
    try {
        google.maps.event.trigger(map, "resize");
    }
    catch(err) {
    }
}

function initializeMapSystem(initial_events) {
    initializeMap();
    updateInitialMapEvents({data: initial_events});
    $('#map_canvas').resize(resize_map);
}
