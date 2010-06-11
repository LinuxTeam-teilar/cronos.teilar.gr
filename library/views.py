# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
from cronos.library.forms import *
from django.shortcuts import render_to_response
from django.template import RequestContext
import httplib
import pycurl
import StringIO
import urllib

def library(request):
	msg = ''
	results = ''
	if request.method == 'GET':
		form = SearchForm(request.GET)
		if form.is_valid():
			link = 'http://hermes.lib.teilar.gr/ipac20/ipac.jsp?session=A26772NR74250.24315&menu=search&aspect=subtab22&npp=40&ipp=20&spp=20&profile=multbl--1&ri=&term=%s&index=.GEN&x=0&y=0&aspect=subtab22' % (str(request.GET.get('search')))
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
				author = ''.join(str(soup.findAll('td')[i+1].contents[0].contents[1:]))[4:-5]
				editor = str(soup.findAll('td')[i+2].contents[0].contents[0]).split(' : ')[1]
				city = str(soup.findAll('td')[i+2].contents[0].contents[0]).split(' : ')[0]
				i += 10
				results.append([title, author, editor, city])
			if (results == []):
				msg = 'Δεν υπάρχουν αποτελέσματα'
	else:
		form = SearchForm()
	return render_to_response('library.html', {
			'form': form,
			'msg': msg,
			'results': results,
		}, context_instance = RequestContext(request))
