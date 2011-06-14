from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson
from google.appengine.api import channel


def map(request):
    token = channel.create_channel('map')
    #return HttpResponse("mapa")
    return render_to_response('gui/map.html', {'token': token})

def send(request):
    message = simplejson.dumps({'msg': 'novo teste'})
    channel.send_message('map', message)
    return HttpResponse("Mensagem enviada")