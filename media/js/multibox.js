$().ready(function() {
	$('#add').click(function() {
		return !$('#id_teacher_announcements option:selected').remove().appendTo('#teacherann_selected');
	});
	$('#remove').click(function() {
		return !$('#teacherann_selected option:selected').remove().appendTo('#id_teacher_announcements');
	});
});
