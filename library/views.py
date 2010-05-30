# -*- coding: utf-8 -*-

import pycurl
import httplib
import urllib
import StringIO
from cronos.library.forms import *
from BeautifulSoup import BeautifulSoup
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import Context
from django.template.loader import get_template

def library(request):
	if request.method == 'GET':
		form = SearchForm(request.GET)
		if form.is_valid():
			link = 'http://hermes.lib.teilar.gr/ipac20/ipac.jsp?session=A26772NR74250.24315&menu=search&aspect=subtab22&npp=10&ipp=20&spp=20&profile=multbl--1&ri=&term=' + str(request.GET.get('search')) + '&index=.GEN&x=0&y=0&aspect=subtab22'
			b = StringIO.StringIO()
			conn = pycurl.Curl()
			conn.setopt(pycurl.URL, link)
			conn.setopt(pycurl.WRITEFUNCTION, b.write)
			conn.perform()
			output = unicode(b.getvalue(), 'utf-8', 'ignore')
			soup = BeautifulSoup(output).findAll('table')[24]
			
			results = []
			results1 = []
			i = 4
			k = 0
			for item in (soup.findAll('a', 'mediumBoldAnchor')):
				results.append([])
				title = str(soup.findAll('td')[i].contents[0].contents[0])
				author = ''
				for j in (soup.findAll('td')[i+1].contents[0].contents):
					author += str(j)
				editor = ''
				for j in (soup.findAll('td')[i+2].contents[0].contents):
					editor += str(j)
				i += 10
				results1 = [title, author, editor]
				for j in xrange(3):
					results[k].append(results1[j][:])
				k +=  1

			if (results == []):
				search = 'empty'
			else:
				search = 'set'

			template = get_template('library.html')
			variables = Context({
				'search': search,
				'results': results,
			})
			output = template.render(variables)
			return HttpResponse(output)
	else:
		form = SearchForm()
	return render_to_response('library.html', {'form': form, } )
