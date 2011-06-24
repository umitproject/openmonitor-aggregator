from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson
from google.appengine.api import channel
from events.models import Event, EventType, EventLocation, TargetType
import datetime
from geopy import geocoders

def map(request):
    token = channel.create_channel('realtimebox')
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

def send(request):
    g = geocoders.Google("ABQIAAAAWajWEMOvdMUzDSviTnY9_BQCULP4XOMyhPd8d_NrQQEO8sT8XBSloh91HGZYV6pQ4yQ1gkhp8E4bJw")
    event = Event()
    event.targetType = TargetType.Website
    event.eventType = EventType.Offline
    event.firstDetectionUTC = datetime.datetime(2011,06,24,11,00)
    event.lastDetectionUTC = datetime.datetime(2011,06,24,11,32)
    event.active = True
    event.target = "www.twitter.com"
    event.save()

    location1 = EventLocation()
    location1.city = "Aveiro"
    location1.country = "Portugal"
    location1.event = event
    (place, point) = g.geocode(location1.city + ", " + location1.country)
    location1.latitude = point[0]
    location1.longitude = point[1]
    location1.save()

    location2 = EventLocation()
    location2.city = "Leiria"
    location2.country = "Portugal"
    location2.event = event
    (place, point) = g.geocode(location2.city + ", " + location2.country)
    location2.latitude = point[0]
    location2.longitude = point[1]
    location2.save()
    
    message = simplejson.dumps(event.getDict())
    channel.send_message('realtimebox', message)
    #channel.send_message('map', message)
    return HttpResponse("Event sent")