from django.shortcuts import render_to_response
from django.utils import simplejson
from google.appengine.api import channel
from events.models import Event

def map(request):
    token = channel.create_channel('map')
    events = Event.getActiveEvents()
    events_dict = []
    for event in events:
        events_dict.append(event.getDict())
    initialEvents = simplejson.dumps(events_dict)
    return render_to_response('notificationsystem/map.html', {'token': token, 'initial_events': initialEvents})

def realtimebox(request):
    token = channel.create_channel('realtimebox')
    events = Event.getActiveEvents()
    events_dict = []
    for event in events:
        events_dict.append(event.getDict())
    initialEvents = simplejson.dumps(events_dict)
    return render_to_response('notificationsystem/realtimebox.html', {'token': token, 'initial_events': initialEvents})

def event(request, event_id):
    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        raise Http404
    return render_to_response('events/event.html', event.getFullDict())