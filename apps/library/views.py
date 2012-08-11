# -*- coding: utf-8 -*-

from apps.library.forms import LibraryForm
from apps.teilar.websites_login import teilar_login
from bs4 import BeautifulSoup
from django.shortcuts import render_to_response
from django.template import RequestContext

def library(request):
    '''
    Perform search in library.teilar.gr and print the results
    '''
    msg = None
    if request.method == 'GET':
        form = LibraryForm(request.GET)
        if form.is_valid():
            link = 'http://hermes.lib.teilar.gr/ipac20/ipac.jsp?session=A26772NR74250.24315&menu=search&aspect=subtab22&npp=40&ipp=20&spp=20&profile=multbl--1&ri=&term=%s&index=.GEN&x=0&y=0&aspect=subtab22' % str(request.GET.get('search'))
            output = teilar_login(link)
            soup = BeautifulSoup(output).find_all('table')[24]
            results = []
            temp_a_mediumboldanchor = soup.find_all('a', 'mediumBoldAnchor')
            temp_td = soup.find_all('td')
            i = 5
            for item in temp_a_mediumboldanchor:
                title = item.contents[0]
                '''
                The authors are in <i> tags. Take the list of them by
                taking a list of the contents of <i> tags, and then
                join the list with commas for prettier output
                '''
                authors = []
                tmp_authors = temp_td[i].find_all('i')
                for author in tmp_authors:
                    authors.append(author.contents[0].replace(',', '').strip())
                authors = ', '.join(authors)
                editor = temp_td[i+1].contents[0].contents[0].split(' : ')[1]
                city = temp_td[i+1].contents[0].contents[0].split(' : ')[0]
                i += 10
                results.append([title, authors, editor, city])
            if not results:
                msg = 'Δεν υπάρχουν αποτελέσματα'
    else:
        form = SearchForm()
    return render_to_response('library.html', {
            'form': form,
            'msg': msg,
            'results': results,
        }, context_instance = RequestContext(request))
