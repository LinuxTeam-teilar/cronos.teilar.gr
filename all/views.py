from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template

def all(request):
	template = get_template('all.html')
	variables = Context({ 'head_title': 'poseidon.teilar.gr' })
	output = template.render(variables)
	return HttpResponse(output)
