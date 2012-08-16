function renderTemplate(template, context) {
   /* Render a basic Django template string (variables only) 
      with context given as JS object */
 
   var text = new String(template);
   for (var key in context) {
     var value = context[key];
     var patt = new RegExp("[{][{][ ]*"+key+"[ ]*[}][}]", "g");
     text = text.replace(patt, value);
   };
   return text;
}

function getFullLocationNameString(location) {
	if (location.location_country_name == 'Unknown')
		return 'Unknown';
	else {
        if(location.location_name!="")
            var location_name = location.location_name + ", ";
        else
        	var location_name = "";
        location_name += location.location_country_name;
        return location_name;
	}
}

function getPosition(who){
    var T= 0,L= 0;
    while(who){
        L += who.offsetLeft;
        T += who.offsetTop;
        who = who.offsetParent;
    }
    return [L,T];
}


function get_size() {
    var winW = 0;
    var winH = 500;
    if (document.body && document.body.offsetWidth) {
        winW = document.body.offsetWidth;
        winH = document.body.offsetHeight;
    }
    if (document.compatMode=='CSS1Compat' &&
        document.documentElement &&
        document.documentElement.offsetWidth ) {
        winW = document.documentElement.offsetWidth;
        winH = document.documentElement.offsetHeight;
    }
    if (window.innerWidth && window.innerHeight) {
        winW = window.innerWidth;
        winH = window.innerHeight;
    }
    return [winW, winH];
}


function formatDate(dateStr)
{
    date = new Date(dateStr);
    return date.format("dd/mm/yyyy HH:MM:ss");
}


function resize_content() {
    // we shouldn't use jQuery to calculate fast on first load
    var win_size = get_size();
    var content_div = document.getElementById('content');
    var content_height = win_size[1] - getPosition(content_div)[0]

    var footer_starter_div = document.getElementById('footer-starter');
    var footer_ender_div = document.getElementById('footer-ender');
    
    var footer_height = getPosition(footer_ender_div)[1] - getPosition(footer_starter_div)[1];
    content_height = content_height - footer_height - 70;
    content_div.style.height = content_height+'px';

    var map_div = document.getElementById('map_canvas');
    if (map_div) {
        map_div.style.height = content_height+'px';
    }

    var realtimebox_div = document.getElementById('left-bar');
    if (realtimebox_div) {
        realtimebox_div.style.height = content_height+'px';
        events_box_div = document.getElementById('events-box');
        if (events_box_div)
            events_box_div.style.display = '';
    }
}


$.ajaxSetup({
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                 if (cookie.substring(0, name.length + 1) == (name + '=')) {
                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                     break;
                 }
             }
         }
         return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     }
});

(function (){
    $(window).resize(resize_content);
})()
