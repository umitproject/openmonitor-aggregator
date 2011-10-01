function send_suggestion(suggestion_type, form_data) {
	$.ajax({
		url: "/suggest_"+suggestion_type,
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
	if ($('#website_suggest_form').length > 0) {
		$("#website_suggest_form").submit(function () {
			set_msg("");
			set_errors(null);
			
			var website = $('#id_website').val();
			var region = $('#id_region').val();
			
			if (website == '') {
				set_msg("You must fill in at least a website");
				return false;
			}
			
			send_suggestion('website',
							{website:website,
							 region:region});
			
			return false;
		});
	}
	
	if ($('#service_suggest_form').length > 0) {
		$("#service_suggest_form").submit(function () {
			set_msg("");
			set_errors(null);
			
			var host = $('#id_host').val();
			var service = $('#id_service').val();
			var port = $('#id_port').val();
			var region = $('#id_region').val();
			
			if (host == '' || service == '' || port == '') {
				set_msg("You must fill in a host name, service name and port at least.");
				return false;
			}
			
			send_suggestion('service',
							{host_name:$('#id_host_name').val(),
							 service_name:$('#id_service_name').val(),
							 port:$('#id_port').val(),
							 region:$('#id_region').val()});
			
			return false;
		});
	}
});