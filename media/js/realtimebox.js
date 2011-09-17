function addEventToList(event, appear)
{
    eventdiv = $( document.createElement('div') )
    content = "<a href='" + event.url + "'>" + event.targetType + " " + event.type + " " + event.target + "</a><br />First Detection: " + formatDate(event.firstdetection) + "<br />Last Detection: " + formatDate(event.lastdetection) + "<br />Location: ";
    for(i=0; i<event.locations.length; i++)
    {
        if(event.locations[i].city!="")
            content += event.locations[i].city + ", ";
        content += event.locations[i].country;
        if(i!=event.locations.length-1)
            content += "; ";
    }
    eventdiv.addClass("event").html(content)

    if(event.active)
        eventdiv.addClass("active")
    $("#realtime_content").prepend(eventdiv)

    if(appear)
    {
        eventdiv.hide()
        eventdiv.slideDown("slow")
    }

    // TODO: format information; show all information
}

function onRealTimeOpened() {
    $("#realtime_status").html("Waiting for new events")
};

function onRealTimeMessage(m) {
    event = JSON.parse(m.data)
    $("#realtime_status").html("New event")
    addEventToList(event, true)
}

function onRealTimeError() {
    $("#realtime_status").html("Error loading events")
}

function onRealTimeChannelOpen() {
    var token = '{{ token }}';
    var channel = new goog.appengine.Channel(token);
    var handler = {
      'onopen': onRealTimeOpened,
      'onmessage': onRealTimeMessage,
      'onerror': onRealTimeError,
      'onclose': function() {}
    };
    var socket = channel.open(handler);
    socket.onopen = onRealTimeOpened;
    socket.onmessage = onRealTimeMessage;
    socket.onerror = onRealTimeError;
}

updateInitialRealTimeEvents = function(m)
{
    events = JSON.parse(m.data)
    for(var i=0; i<events.length; i++)
    {
        addEventToList(events[i], false)
    }
}

function initializeRealTime() {
    openChannel();
    updateInitialEvents({data: '{{ initial_events|safe }}'});
}

$(document).load(initializeRealTime);
