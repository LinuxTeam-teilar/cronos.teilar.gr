# -*- coding: utf-8 -*-

import os
import sys
from proj_root import PROJECT_ROOT
sys.path.append(PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.settings'
from apps import CronosError, log_extra_data
from apps.teilar.websites_login import teilar_login
from bs4 import BeautifulSoup
from datetime import date
from django.utils import feedgenerator
import logging

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

'''
This is a temporary lib that creates RSS feeds for the following websites of teilar
that either provide a bad RSS or don't provide one at all:
- http://teilar.gr/news.php?cid=1
- http://teilar.gr/news.php?cid=2
- http://teilar.gr/news.php?cid=5
- http://teilar.gr/news.php?cid=6
- http://teilar.gr/tmimatanews.php
'''

def various_teilar():
    '''
    Initialize custom_rss
    '''
    custom_rss_path = '/tmp/custom_teilar_announcements.rss'
    custom_rss = feedgenerator.Rss201rev2Feed(
        title = 'custom',
        link = 'custom',
        description = 'custom',
        author_name = 'custom'
    )

    for cid in [1, 2, 5, 6, 'tmimatanews.php']:
        '''
        Grab announcements for the following websites and
        put them in a custom RSS file:
         - http://teilar.gr/news.php?cid=1
         - http://teilar.gr/news.php?cid=2
         - http://teilar.gr/news.php?cid=5
         - http://teilar.gr/news.php?cid=6
         - http://teilar.gr/tmimatanews.php
        '''
        if cid == 1:
            author = u'Γενικές Ανακοινώσεις'
        elif cid == 2:
            author = u'Ανακοινώσεις του ΤΕΙ Λάρισας'
        elif cid == 5:
            author = u'Συνεδριάσεις Συμβουλίου ΤΕΙ Λάρισας'
        elif cid == 6:
            author = u'Ανακοινώσεις της Επιτροπής Εκπαίδευσης και Ερευνών του ΤΕΙ Λάρισας'
        else:
            author = None
        if type(cid) == int:
            output = teilar_login('teilar', 'news.php?cid=%s' % cid)
        else:
            output = teilar_login('teilar', cid)
        '''
        Parse the urlid of the announcement
        '''
        soup = BeautifulSoup(output)
        try:
            announcements_all = soup.find_all('table')[17].find_all('a', 'BlackText11')
            announcement = {}
            for item in announcements_all[::-1]:
                announcement['urlid'] = item['href'].split('nid=')[1]
                '''
                Get inside the announcement to get the rest of the info
                '''
                ann_link = 'news_detail.php?nid=' + announcement['urlid']
                if type(cid) != int:
                    ann_link = 'tmimata/' + ann_link
                output = teilar_login('teilar', ann_link)
                soup = BeautifulSoup(output)
                if not author:
                    author_name = soup.find('span', 'OraTextBold').contents[0].split(' >')[0].replace(u'Τεχν.', u'Τεχνολογίας')
                else:
                    author_name = author
                temp_td_oratext = soup.find_all('td', 'OraText')
                pubdate = temp_td_oratext[0].contents[0].split('/')
                pubdate = date(int(date[2]), int(date[1]), int(date[0]))
                title = temp_td_oratext[1].contents[0]
                description = soup.find('td', 'BlackText11').contents[0]
                try:
                    # TODO: A list of cases for known mimetypes eg .doc
                    enclosure = feedgenerator.Enclosure(soup.find('a', 'BlackText11Bold')['href'], 'Unknown', 'Unknown')
                except:
                    enclosure = None
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data())
            logger_mail.exception(error)
            raise CronosError(u'Παρουσιάστησε σφάλμα κατά το scraping των ανακοινώσεων')
        add_rss_item(custom_rss, title, 'http://teilar.gr/' + ann_link, date, description, author_name, attachment)
    write_rss_file(custom_rss, custom_rss_path)
    return

def add_rss_item(custom_rss, title, link, pubdate, description, author_name, enclosure):
    '''
    Write the item in the RSS feed
    '''
    custom_rss.add_item(
        title = title,
        link = link,
        pubdate = pubdate,
        description = description,
        author_name = author_name,
        enclosure = enclosure,
    )
    return

def write_rss_file(custom_rss, path):
    '''
    Write the RSS in a file
    '''
    try:
        teilarfeed = open(path, 'w')
        custom_rss.write(teilarfeed, 'UTF-8')
        teilarfeed.close()
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data())
        logger_mail.exception(error)
        raise CronosError(u'Παρουσιάστησε σφάλμα κατά την εγγραφή του RSS σε αρχείο')
    return

if __name__ == '__main__':
    try:
        various_teilar()
    except CronosError as error:
        logger_syslog.error(error.value, extra = log_extra_data())
