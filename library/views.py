# -*- coding: utf-8 -*-

import pycurl
import httplib
import urllib
import StringIO
from cronos.library.forms import *
from BeautifulSoup import BeautifulSoup
from django.shortcuts import render_to_response
from django.template import RequestContext

def library(request):
	msg = ''
	results = ''
	if request.method == 'GET':
		form = SearchForm(request.GET)
		if form.is_valid():
			link = 'http://hermes.lib.teilar.gr/ipac20/ipac.jsp?session=A26772NR74250.24315&menu=search&aspect=subtab22&npp=10&ipp=20&spp=20&profile=multbl--1&ri=&term=%s&index=.GEN&x=0&y=0&aspect=subtab22' % (str(request.GET.get('search')))
			b = StringIO.StringIO()
			conn = pycurl.Curl()
			conn.setopt(pycurl.URL, link)
			conn.setopt(pycurl.WRITEFUNCTION, b.write)
			conn.perform()
			output = unicode(b.getvalue(), 'utf-8', 'ignore')
			soup = BeautifulSoup(output).findAll('table')[24]
			results = []
			i = 4
			k = 0
			for item in (soup.findAll('a', 'mediumBoldAnchor')):
				title = str(soup.findAll('td')[i].contents[0].contents[0])
				author = ''
				for j in (soup.findAll('td')[i+1].contents[0].contents):
					author += str(j)
				editor = ''
				for j in (soup.findAll('td')[i+2].contents[0].contents):
					editor += str(j)
				i += 10
				results.append([title, author, editor])
			if (results == []):
				msg = 'Δεν υπάρχουν αποτελέσματα'
	else:
		form = SearchForm()
	return render_to_response('library.html', {
			'head_title': 'Βιβλιοθήκη | ',
			'form': form,
			'msg': msg,
			'results': results,
		}, context_instance = RequestContext(request))
