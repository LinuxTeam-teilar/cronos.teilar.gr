from django.http import HttpResponse
from django.template import Context
from django.template.loader import get_template

def sidebar(request):
	template = get_template('sidebar.html')
	variables = Context({ 'title': 'welcome' })
	output = template.render(variables)
	return HttpResponse(output)
