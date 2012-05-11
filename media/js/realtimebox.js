var EVENT_SUMMARY_TEMPLATE = " \
  <strong> {{ event_target_type }} {{ event_type }} </strong>\
  <br />First Detection: {{ first_detection }}\
  <br />Last Detection: {{ last_detection }}\
  <br />Locations: {{ locations }}\
";

function receiveEvents(token, events){
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

function onMapOpened() {
	$("#map_status").html("Waiting for events...")
};

function onMapMessage(m) {
	event = JSON.parse(m.data);

	addEventToMap(event, true);
	addEventToList(event, true);
}

function onMapError(error) {
	//alert(error);
	//console.debug(error);
	$("#map_status").html("Error loading events")
}

function addEventToList(event, appear)
{
    event_div = $(document.createElement('div'))
    locations = ""
    for(i=0; i<event.locations.length; i++)
    {
        if(event.locations[i].location_name!="")
            locations += event.locations[i].location_name + ", ";
        locations += event.locations[i].location_country_name;
        if(i!=event.locations.length-1)
            locations += "; ";
    }
    context = {
    	      'event_url' : event.url,
    	      'event_target_type': event.targetType,
    	      'event_type': event.type,
    	      'event_target': event.target,
    	      'first_detection': formatDate(event.firstdetection),
    	      'last_detection': formatDate(event.lastdetection),
    	      'locations': locations,
    	    };
    
    content_to_add = renderTemplate(EVENT_SUMMARY_TEMPLATE, context);

    event_div.addClass("alert alert-error event-info");
    event_div.html(content_to_add);
    $("#events-box").prepend(event_div);
    
    if (appear) {
    	event_div.hide();
    	event_div.slideDown();
    }

    // TODO: format information; show all information
}

updateInitialRealTimeEvents = function(m)
{
    events = JSON.parse(m.data)
    for(var i=0; i<events.length; i++)
    {
        addEventToList(events[i], false)
    }
}

function initializeRealTime(initial_events) {
    updateInitialRealTimeEvents({data: initial_events});
}
