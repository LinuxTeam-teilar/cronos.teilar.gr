from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template

def main(request) :
	template = get_template('main.html')
	variables = Context({
		'head_title': 'poseidon.teilar.gr',
	})
	output = template.render(variables)
	return HttpResponse(output)
