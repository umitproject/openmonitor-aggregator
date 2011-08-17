from django.conf.urls.defaults import *
from piston.resource import Resource
from api.handlers import *

registeragent_handler = Resource(RegisterAgentHandler)
getpeerlist_handler = Resource(GetPeerListHandler)
getsuperpeerlist_handler = Resource(GetSuperPeerListHandler)
getevents_handler = Resource(GetEventsHandler)
sendwebsitereport_handler = Resource(SendWebsiteReportHandler)
sendservicereport_handler = Resource(SendServiceReportHandler)
checkversion_handler = Resource(CheckNewVersionHandler)
checktests_handler = Resource(CheckNewTestHandler)
websitesuggestion_handler = Resource(WebsiteSuggestionHandler)
servicesuggestion_handler = Resource(ServiceSuggestionHandler)
test_handler = Resource(TestsHandler)
checkaggregator_handler = Resource(CheckAggregator)
login_handler = Resource(LoginHandler)
logout_handler = Resource(LogoutHandler)

urlpatterns = patterns('',
   url(r'^registeragent/$', registeragent_handler),
   url(r'^loginagent/$', login_handler),
   url(r'^logoutagent/$', logout_handler),
   url(r'^getpeerlist/$', getpeerlist_handler),
   url(r'^getsuperpeerlist/$', getsuperpeerlist_handler),
   url(r'^getevents/$', getevents_handler),
   url(r'^sendwebsitereport/$', sendwebsitereport_handler),
   url(r'^sendservicereport/$', sendservicereport_handler),
   url(r'^checkversion/$', checkversion_handler),
   url(r'^checktests/$', checktests_handler),
   url(r'^websitesuggestion/$', websitesuggestion_handler),
   url(r'^servicesuggestion/$', servicesuggestion_handler),
   url(r'^tests/$', test_handler),
   url(r'^checkaggregator/$', checkaggregator_handler),
   url(r'^$', checkaggregator_handler),
)