$().ready(function() {
	$('#add1').click(function() {
		return !$('#teachers_unselected option:selected').remove().appendTo('#teachers_selected');
	});
	$('#remove1').click(function() {
		return !$('#teachers_selected option:selected').remove().appendTo('#teachers_unselected');
	});
	$('#add2').click(function() {
		return !$('#websites_unselected option:selected').remove().appendTo('#websites_selected');
	});
	$('#remove2').click(function() {
		return !$('#websites_selected option:selected').remove().appendTo('#websites_unselected');
	});
	$('#announcements').submit(function() {
		$('#teachers_selected option').each(function(i) {
			$(this).attr("selected", "selected");
		});
		$('#websites_selected option').each(function(i) {
			$(this).attr("selected", "selected");
		});
	});
});
