function send_event(event_type, form_data) {
	$.ajax({
		url: "/create_"+event_type+"_event",
		data: form_data,
		dataType: "json",
		type: "POST",
		success: function(data){
			set_msg(data['msg']);
			set_errors(data['errors']);
		},
	})
}


function set_msg(message) {
	var msg = $('#msg');
	msg.html(message);
	msg.fadeIn();
}

function set_errors(errors) {
	error_div = $('#error');
	
	if (errors != null) {
		for (var error in errors) {
			if (errors.hasOwnProperty(error)) {
				for (var e in errors[error]) {
					error_div.append(" - "+error+": "+errors[error][e]);
				}
			}
		}
		error_div.fadeIn();
	} else {
		error_div.html('');
		error_div.fadeOut();
	}
	
}


$(document).ready(function () {
	if ($('#website_event_form').length > 0) {
		$("#website_event_form").submit(function () {
			set_msg("");
			set_errors(null);
			
			var website = $('#id_website').val();
			var location = $('#id_location').val();
            var first_detection = $('#id_first_detection').val();
            var event_type = $('#id_event_type').val();
			
			if (website == '') {
				set_msg("You must fill in at least a website");
				return false;
			}
			
			send_event('website',
							{website:website,
							 location:location,
                             first_detection:first_detection,
                             event_type:event_type});
			
			return false;
		});
	}
	
	if ($('#service_event_form').length > 0) {
		$("#service_event_form").submit(function () {
			set_msg("");
			set_errors(null);
			
			var service = $('#id_service').val();
			var location = $('#id_location').val();
            var first_detection = $('#id_first_detection').val();
            var event_type = $('#id_event_type').val();

			if (service == '') {
				set_msg("You must fill in at least a service name");
				return false;
			}

			send_event('service',
							{service:service,
							 location:location,
                             first_detection:first_detection,
                             event_type:event_type});
			
			return false;
		});
	}
});