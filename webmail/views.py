# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
from cronos.libraries.encryption import decryptPassword
from cronos.libraries.login import *
from cronos.webmail.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render_to_response
from django.template import RequestContext

@login_required
def webmail(request):
    id = ''
    if (request.GET.get('passed_id')):
        form = MailForm(request.GET)
        link = 'http://myweb.teilar.gr/src/read_body.php?mailbox=INBOX&passed_id=' + str(request.GET.get('passed_id')) + '&startMessage=1&show_more=1'
        output = webmail_login(link, request.user.get_profile().webmail_username, decryptPassword(request.user.get_profile().webmail_password))
        soup = BeautifulSoup(output)
        title = soup.findAll('td')[10].contents[0]
        sender = soup.findAll('td')[12].contents[0]
        date = soup.findAll('td')[14].contents[0]
        to = soup.findAll('td')[16].contents[0][:-7]
        try:
            for item in soup.findAll('td')[16].contents[4:]:
                to += str(item)
        except:
            pass
        subject = soup.findAll('table')[7]
        mail = [title, sender, date, to, subject]
        id = request.GET.get('passed_id')
    else:
        form = MailForm()
        link = 'http://myweb.teilar.gr/src/right_main.php?PG_SHOWALL=1&use_mailbox_cache=0&startMessage=1&mailbox=INBOX'
        output = webmail_login(link, request.user.get_profile().webmail_username, decryptPassword(request.user.get_profile().webmail_password))
        soup = BeautifulSoup(output).findAll('table')[9]
        soup1 = soup.findAll('tr')
        mail = []
        k = 0
        for i in xrange(1, len(soup1)):
            if (len(str(soup1[i].find('a'))) > 4):
                sender_name = str(soup1[i].findAll('td')[1].contents[0].contents[0])
                sender_mail = str(soup1[i].findAll('td')[1]).split('"')[5]
                passed_id = str(soup1[i].find('a')).split('&amp;')[1].replace('passed_id=', '')
                time = str(soup1[i].findAll('td')[2].contents[0])
                title = str(soup1[i].findAll('td')[4].a.contents[0])
                try:
                    full_title = str(soup1[i].findAll('td')[4].a).split('"')[3]
                except (TypeError, IndexError):
                    full_title = ''
                mail.append([title, sender_mail, sender_name, time, passed_id])
    return render_to_response('webmail.html', {
            'form': form,
            'items': mail,
            'id': id,
        }, context_instance = RequestContext(request))
