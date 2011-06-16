from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson
from google.appengine.api import channel


def map(request):
    token = channel.create_channel('map')
    return render_to_response('notificationsystem/map.html', {'token': token})

def realtimebox(request):
    token = channel.create_channel('map')
    return render_to_response('notificationsystem/realtimebox.html', {'token': token})

def send(request):
    message = simplejson.dumps({'msg': 'This is a new event'})
    channel.send_message('map', message)
    return HttpResponse("Event sent")