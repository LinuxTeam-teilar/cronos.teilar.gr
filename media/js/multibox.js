$().ready(function() {
	$('#add').click(function() {
		return !$('#id_teacher_announcements option:selected').remove().appendTo('#selected');
	});
	$('#remove').click(function() {
		return !$('#selected option:selected').remove().appendTo('#id_teacher_announcements');
	});
});
