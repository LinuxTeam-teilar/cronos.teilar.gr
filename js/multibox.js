$().ready(function() {
	$('#add1').click(function() {
		return !$('#id_teacher_announcements option:selected').remove().appendTo('#teacherann_selected');
	});
	$('#remove1').click(function() {
		return !$('#teacherann_selected option:selected').remove().appendTo('#id_teacher_announcements');
	});
	$('#teacherann').submit(function() {
		$('#teacherann_selected option').each(function(i) {
			$(this).attr("selected", "selected");
		});
	});
	$('#add2').click(function() {
		return !$('#id_other_announcements option:selected').remove().appendTo('#otherann_selected');
	});
	$('#remove2').click(function() {
		return !$('#otherann_selected option:selected').remove().appendTo('#id_other_announcements');
	});
	$('#otherann').submit(function() {
		$('#otherann_selected option').each(function(i) {
			$(this).attr("selected", "selected");
		});
	});
});
