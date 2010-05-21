from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template

def frames(request) :
	template = get_template('frames.html')
	variables = Context({
		'head_title': 'cronos.teilar.gr',
	})
	output = template.render(variables)
	return HttpResponse(output)
