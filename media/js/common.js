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

function formatDate(dateStr)
{
    date = new Date(dateStr);
    return date.format("dd/mm/yyyy HH:MM:ss");
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
    resize();
});

function resize() {
	window_size = get_size();
	
	resize_page(window_size[0], window_size[1]);
	resize_map(window_size[0], window_size[1]);
	resize_realtimebox(window_size[0], window_size[1]);
}

$(window).resize(resize);

function resize_page(width, height) {
	$("div#page").width(width - scrollbarWidth());
	$("div#page").height(height);
}

function resize_realtimebox(width, height) {
	$('.realtimebox').height(height -
							  $('.subHeader').height() -
							  $('#footer').height() -
							  $('.logo').height() -
							  $('.sideBarTitle').height() - 10);
}

function resize_map(width, height) {
	$('#map_canvas').height(height -
							$('.subHeader').height() -
							$('#footer').height());
	$('#main-copy').height(height -
							$('.subHeader').height() -
							$('#footer').height());
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


/*!
 * jQuery Scrollbar Width v1.0
 * 
 * Copyright 2011, Rasmus Schultz
 * Licensed under LGPL v3.0
 * http://www.gnu.org/licenses/lgpl-3.0.txt
 */
(function($){
	$.scrollbarWidth = function() {
	  if (!$._scrollbarWidth) {
	     var $body = $('body');
	    var w = $body.css('overflow', 'hidden').width();
	    $body.css('overflow','scroll');
	    w -= $body.width();
	    if (!w) w=$body.width()-$body[0].clientWidth; // IE in standards mode
	    $body.css('overflow','');
	    $._scrollbarWidth = w;
	  }
	  return $._scrollbarWidth;
	};
})(jQuery);
