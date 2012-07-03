var WEBSITE_EVENT_SUMMARY_TEMPLATE = " \
  <div class='row-fluid'><span class='pull-right'><i class='icon-time'></i>{{ active_message }}</span></div> \
  <strong> <i class='icon-globe'></i> {{ event_target_type }} {{ event_type }} </strong> \
  <br /><a target='_blank' href='{{ event_target }}'>{{ event_target }}</a> <i class='icon-share'></i>\
  <br /><strong>First Detection: </strong> {{ first_detection }}\
  <br /><strong>Last Detection: </strong> {{ last_detection }}\
  <br /><strong>Locations: </strong>{{ locations }}\
  <br /><div class='extra'> </div>\
  <div class='row-fluid'><a class='pull-right' href='{{ event_url }}'> see details »</a></div> \
";

var EVENT_URLS = new Array(); // array that holds unique URLs for the events

function getLocationsRepresentionString(raw_locations, show_all_countries) {
	    show_all_countries = typeof show_all_countries !== 'undefined' ? show_all_countries : false;

	    locations_string = "";
	    locations = new Array();
	    unknown_country = false; // put unknown country to the end of locations
	    for(i=0; i<raw_locations.length; i++)
	    {
	    	var country_name = raw_locations[i].location_country_name;
	    	if (country_name === 'Unknown') {
	    		unknown_country = true;
	    	}
	    	else {
		    	if (locations.indexOf(country_name) == -1) 
		    		locations.push(country_name);
	    	}
	    }
	    if (unknown_country) {
	    	locations.push('Unknown');
	    }
	    
	    if (show_all_countries) {
	    	locations_string = locations.join(",");
	    }
	    else {
	    	locations_string = locations.slice(0,3).join(',')
	    	if (locations.length > 3)
	    		locations_string += ' and ' + (locations.length - 3) + ' more...'
	    }
	    return locations_string;
}
  
function createEventSummaryDiv(event, show_all_countries) {
	   
	    
	    event_div = $(document.createElement('div'))
	    var locations_string = getLocationsRepresentionString(event.locations, show_all_countries);

	    /* Show only countries in summary
	    for(i=0; i<event.locations.length; i++)
	    {
	        if(event.locations[i].location_name!="")
	            locations += event.locations[i].location_name + ", ";
	        locations += event.locations[i].location_country_name;
	        if(i!=event.locations.length-1)
	            locations += "; ";
	    }
	    */

	    context = {
	    	      'event_url' : event.url,
	    	      'event_target_type': event.targetType,
	    	      'event_type': event.type,
	    	      'event_target': event.target,
	    	      'first_detection': formatDate(event.firstdetection),
	    	      'last_detection': formatDate(event.lastdetection),
	    	      'locations': locations_string,
	    	      'event_url': event.url
	    	    };
	    if (event.active) {
	    	context['active_message'] = 'still occurs';
	    	context['last_detection'] = 'now';
	    	event_div.addClass('alert-warning');
	    }
	    else {
	    	context['active_message'] = 'ended';
	    	event_div.addClass('alert-info');
	    }
	    
	    content_to_add = renderTemplate(WEBSITE_EVENT_SUMMARY_TEMPLATE, context);

	    event_div.addClass("alert  event-info");
	    event_div.html(content_to_add);
	    return event_div;
}

function receiveEvents(){
	/*
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
    socket.onerror = onMapError;*/

    $.ajax({
        url: "/events/poll",
        dataType: "html",
        type: "POST",
        success: function(data){
            updateInitialMapEvents({data: data});
            updateInitialRealTimeEvents({data: data});
            setTimeout('receiveEvents()', 60000); //poll again after 60 sec.
        },
        error: function(data){
            setTimeout('receiveEvents()', 60000); //poll again after 60 sec.
        }
    });
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
	event_div = createEventSummaryDiv(event);
    $("#events-box").prepend(event_div);
    
    if (appear) {
    	event_div.hide();
    	event_div.slideDown();
    }

    // TODO: format information; show all information
}

updateInitialRealTimeEvents = function(m)
{

    events = JSON.parse(m.data);
    for(var i=(events.length-1); i>-1; i--)
    {
        var event = events[i];
        if (EVENT_URLS.indexOf(event['url']) == -1){
            EVENT_URLS.push(event['url']);
            addEventToList(event, false);
            //addEventToMap(event,false);
        }
        else {
            break;
        }
    }
}

function initializeRealTime(initial_events) {
    updateInitialRealTimeEvents({data: initial_events});
}
