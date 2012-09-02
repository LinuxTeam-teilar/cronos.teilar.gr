from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.http import HttpResponseServerError

def about(request):
    '''
    The About webpage
    '''
    return render_to_response('about.html', {},
        context_instance = RequestContext(request))

def server_error(request, template_name='500.html'):
    '''
    500 error handler.
    Override 500 error page, in order to pass STATIC_URL to Context
    '''
    t = loader.get_template(template_name)
    return HttpResponseServerError(t.render(
        RequestContext(request, {'request_path': request.path})))
