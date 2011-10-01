function formatDate(dateStr)
{
    date = new Date(dateStr);
    return date.format("dd/mm/yyyy HH:MM:ss");
}

$(document).ready(function () {
	if ($('#id_region').length > 0) {
		$("#id_region").autocomplete({
			source:function(req, add) {
						$.getJSON("/a/regions/",
								  { prefix:req.term },
								  function(data){ add(data); });
					}
		});
	}
});