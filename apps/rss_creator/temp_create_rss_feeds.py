# -*- coding: utf-8 -*-

import os
import sys
from proj_root import PROJECT_ROOT
sys.path.append(PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.settings'
from apps import CronosError, log_extra_data
from apps.rss_creator.models import AnnouncementsTeilar
from apps.teilar.websites_login import teilar_login
from bs4 import BeautifulSoup
from datetime import date as proper_date
from django.utils import feedgenerator
import logging

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

'''
This is a temporary lib that creates RSS feeds for the teachers and some other
webpages of teilar.gr that don't provide an RSS yet.
'''

f = feedgenerator.Rss201rev2Feed(title = 'test', link = 'test', description = 'test', author_name = 'test')

'''
Grab a list of urlids from the announcements that are in the DB already
'''
announcements_from_db = []
announcements_from_db_q = AnnouncementsTeilar.objects.all()
for announcement in announcements_from_db_q:
    announcements_from_db.append(announcement.urlid)

for cid in [1, 2, 5, 6, 'tmimatanews.php']:
    '''
    Grab announcements for the following websites and
    put them in the DB:
     - http://teilar.gr/news.php?cid=1
     - http://teilar.gr/news.php?cid=2
     - http://teilar.gr/news.php?cid=5
     - http://teilar.gr/news.php?cid=6
     - http://teilar.gr/tmimatanews.php
    '''
    if cid == 1:
        author_global = u'Γενικές Ανακοινώσεις'
    elif cid == 2:
        author_global = u'Ανακοινώσεις του ΤΕΙ Λάρισας'
    elif cid == 5:
        author_global = u'Συνεδριάσεις Συμβουλίου ΤΕΙ Λάρισας'
    elif cid == 6:
        author_global = u'Ανακοινώσεις της Επιτροπής Εκπαίδευσης και Ερευνών του ΤΕΙ Λάρισας'
    else:
        author_global = None
    if type(cid) == int:
        output = teilar_login('teilar', 'news.php?cid=%s' % cid)
    else:
        output = teilar_login('teilar', cid)
    '''
    Parse the urlid of the announcement
    '''
    soup = BeautifulSoup(output)
    announcements_all = soup.find_all('table')[17].find_all('a', 'BlackText11')
    announcement = {}
    for item in announcements_all[::-1]:
        announcement['urlid'] = item['href'].split('nid=')[1]
#        if int(announcement['urlid']) in announcements_from_db:
#            '''
#            If the announcement is already in the DB skip it
#            '''
            #continue
#            print 'continue'
        '''
        Get inside the announcement to get the rest of the info
        '''
        ann_link = 'news_detail.php?nid='
        if type(cid) != int:
            ann_link = 'tmimata/' + ann_link
        output = teilar_login('teilar', ann_link + announcement['urlid'])
        soup = BeautifulSoup(output)
        if not author_global:
            author = soup.find('span', 'OraTextBold').contents[0].split(' >')[0].replace(u'Τεχν.', u'Τεχνολογίας')
        else:
            author = author_global
        temp_td_oratext = soup.find_all('td', 'OraText')
        date = temp_td_oratext[0].contents[0].split('/')
        date = proper_date(int(date[2]), int(date[1]), int(date[0]))
        title = temp_td_oratext[1].contents[0]
        summary = soup.find('td', 'BlackText11').contents[0]
        try:
            attachment = soup.find('a', 'BlackText11Bold')['href']
        except:
            attachment = None
        '''
        Add the announcement in DB
        '''
        '''announcement_teilar = AnnouncementsTeilar(
            urlid = int(announcement['urlid']),
            author = unicode(author),
            title = unicode(title),
            date = date,
            summary = unicode(summary),
            attachment = attachment,
        )
        try:
            announcement_teilar.save()
            status = u'Επιτυχής προσθήκη της ανακοίνωσης %s' % title
            logger_syslog.info(status, extra = log_extra_data(cronjob = author))
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data(cronjob = author))
            logger_mail.exception(error)
            raise CronosError(u'Παρουσιάστηκε σφάλμα κατά την προσθήκη της ανακοίνωσης %s' % title)'''
        '''
        Add item to feed
        '''
        if attachment:
            attachment = feedgenerator.Enclosure(attachment, 'doc', 'test')
        f.add_item(title = title, link = announcement['urlid'], pubdate = date, description = summary, author_name = author, enclosure = attachment)
teilarfeed = open('/tmp/announcements_teilar.rss', 'w')
f.write(teilarfeed, 'UTF-8')
teilarfeed.close()
