var map
var mapCluster
var eventLvl1 = "/images/alert1.png"
var eventLvl2 = "/images/alert2.png"
var eventLvl3 = "/images/alert3.png"
var newevent  = "/images/newevent.gif"
var newEventTime = 2000

function initializeMap()
{
    var latlng = new google.maps.LatLng(0, 0);
    var myOptions = {
        zoom: 2,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP
    };
    map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);

    var mcOptions = {gridSize: 50, maxZoom: 14};
    mapCluster = new MarkerClusterer(map, [], mcOptions);
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
        title:"Shutdown!",
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
    baseInfo = "<a href='" + event.url + "'>" + event.targetType + " " + event.type + " " + event.target + "</a><br />First Detection: " + formatDate(event.firstdetection) + "<br />Last Detection: " + formatDate(event.lastdetection) + "<br />Location: ";

    for(i=0; i<event.locations.length; i++)
    {
        localInfo = "";
        if(event.locations[i].city!="")
            localInfo = event.locations[i].city + ", ";
        localInfo += event.locations[i].country;

        eventInfo = baseInfo + localInfo;

        placeNewEvent(event.type, eventInfo, event.locations[i].lat, event.locations[i].lng, appear)
    }
    // TODO: format information; show all information
}

function onMapOpened() {
    $("#map_status").html("Waiting for events...")
};

function onMapMessage(m) {
    event = JSON.parse(m.data)
    //$("#map_status").html("New event")
    addEventToMap(event, true)
}

function onMapError(error) {
    alert(error);
    console.debug(error);
    $("#map_status").html("Error loading events")
}

function onMapOpenChannel(token) {
    var channel = new goog.appengine.Channel(token);
    var handler = {
      'onopen': onMapOpened,
      'onmessage': onMapMessage,
      'onerror': onMapError,
      'onclose': function() {}
    };
    var socket = channel.open(handler);
    socket.onopen = onMapOpened;
    socket.onmessage = onMapMessage;
    socket.onerror = onMapError;
}

function updateInitialMapEvents(m)
{
    events = JSON.parse(m.data)
    for(var i=0; i<events.length; i++)
    {
        addEventToMap(events[i], false)
    }
}

function initializeMapSystem(token, initial_events) {
    initializeMap();
    //onMapOpenChannel(token);
    //updateInitialMapEvents({data: initial_events});
}
