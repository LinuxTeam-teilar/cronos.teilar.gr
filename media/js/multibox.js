$().ready(function() {
	$('#add').click(function() {
		return !$('#id_teacher_announcements option:selected').remove().appendTo('#teacherann_selected');
	});
	$('#remove').click(function() {
		return !$('#teacherann_selected option:selected').remove().appendTo('#id_teacher_announcements');
	});
	$('form').submit(function() {
		$('#teacherann_selected option').each(function(i) {
			$(this).attr("selected", "selected");
		});
	});
});
