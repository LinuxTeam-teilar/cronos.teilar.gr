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
from django.conf import settings
from django.utils import feedgenerator
import logging

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

'''
This is a temporary lib that creates RSS feeds for websites of teilar.gr
that either provide a bad RSS or don't provide one at all
'''

def initialize_rss_file():
    '''
    Create a custom_rss object with dummy headers
    '''
    custom_rss = feedgenerator.Rss201rev2Feed(
        title = 'custom',
        link = 'custom',
        description = 'custom',
        author_name = 'custom'
    )
    return custom_rss

def add_rss_item(custom_rss, title, link, pubdate, description, author_name, enclosure):
    '''
    Append an item in the RSS feed
    '''
    try:
        custom_rss.add_item(
            title = title,
            link = link,
            pubdate = pubdate,
            description = description,
            author_name = author_name,
            enclosure = enclosure,
        )
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(title))
        logger_mail.exception(error)
        raise CronosError(u'Παρουσιάστηκε σφάλμα κατά την προσθήκη στοιχείου στο RSS')
    return

def write_rss_file(custom_rss, filename):
    '''
    Write the RSS in a file
    '''
    try:
        if not os.path.exists(settings.RSS_PATH):
            '''
            Create the dir if it doesn't exist
            '''
            os.makedirs(settings.RSS_PATH)
        teilarfeed = open('%s/%s' % (settings.RSS_PATH, filename), 'w')
        custom_rss.write(teilarfeed, 'UTF-8')
        teilarfeed.close()
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data())
        logger_mail.exception(error)
        raise CronosError(u'Παρουσιάστησε σφάλμα κατά την εγγραφή του RSS σε αρχείο')
    return

def get_teilar():
    '''
    Grab announcements from the following websites and
    put them in a custom RSS file:
    - http://teilar.gr/news.php?cid=1
    - http://teilar.gr/news.php?cid=2
    - http://teilar.gr/news.php?cid=5
    - http://teilar.gr/news.php?cid=6
    - http://teilar.gr/tmimatanews.php
    '''
    for cid in [1, 2, 5, 6, 'tmimatanews.php']:
        custom_rss = initialize_rss_file()
        if cid == 1:
            rss_name = u'general.rss'
        elif cid == 2:
            rss_name = u'teilar_ann.rss'
        elif cid == 5:
            rss_name = u'council.rss'
        elif cid == 6:
            rss_name = u'committee.rss'
        else:
            rss_name = u'departments.rss'
        if type(cid) == int:
            output = teilar_login('http://www.teilar.gr/news.php?cid=%s' % cid)
        else:
            output = teilar_login('http://www.teilar.gr/%s' % cid)
        '''
        Parse the urlid of the announcement
        '''
        soup = BeautifulSoup(output)
        try:
            announcements_all = soup.find_all('table')[17].find_all('a', 'BlackText11')[:10]
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data())
            logger_mail.exception(error)
            raise CronosError(u'Παρουσιάστηκε σφάλμα κατά την ανάκτηση ανακοινώσεων')
        for item in announcements_all:
            '''
            Get inside the announcement to get the rest of the info
            '''
            ann_link = 'news_detail.php?nid=' + item['href'].split('nid=')[1]
            if type(cid) != int:
                ann_link = 'tmimata/' + ann_link
            output = teilar_login('http://www.teilar.gr/%s' % ann_link)
            soup = BeautifulSoup(output)
            try:
                if type(cid) != int:
                    creator = soup.find('span', 'OraTextBold').contents[0].split(' >')[0].replace(u'Τεχν.', u'Τεχνολογίας')
                else:
                    creator = None
                temp_td_oratext = soup.find_all('td', 'OraText')
                pubdate = temp_td_oratext[0].contents[0].split('/')
                pubdate = date(int(pubdate[2]), int(pubdate[1]), int(pubdate[0]))
                title = temp_td_oratext[1].contents[0]
                description = soup.find('td', 'BlackText11').contents[0]
                try:
                    # TODO: A list of cases for known mimetypes eg .doc
                    enclosure = feedgenerator.Enclosure(soup.find('a', 'BlackText11Bold')['href'], 'Unknown', 'Unknown')
                except:
                    enclosure = None
            except Exception as error:
                logger_syslog.error(error, extra = log_extra_data('http://teilar.gr' + ann_link))
                logger_mail.exception(error)
                raise CronosError(u'Παρουσιάστηκε σφάλμα κατά την ανάκτηση ανακοίνωσης')
            add_rss_item(custom_rss, title, 'http://teilar.gr/' + ann_link, pubdate, description, creator, enclosure)
        write_rss_file(custom_rss, rss_name)
    return

def get_teachers():
    '''
    Grab announcements from all the teachers, and put them in
    a custom RSS file.
    '''
    custom_rss = initialize_rss_file()
    output = teilar_login('http://www.teilar.gr/profannnews.php')
    soup = BeautifulSoup(output)
    try:
        announcements_all = soup.find_all('a', 'BlackText11')
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data())
        logger_mail.exception(error)
        raise CronosError(u'Παρουσιάστηκε σφάλμα κατά την ανάκτηση ανακοινώσεων καθηγητών')
    authors = {}
    for item in announcements_all:
        '''
        The teacher's announcements are all under one page instead
        of being each one in separate page. We count in the combined
        page how many times a teacher's name is mentioned, and we
        parse the same number of the teacher's top announcements.
        The results are kept in a dictionary with the following structure:
        authors = {'link': number_of_announcements}
        '''
        link = item['href']
        if link in authors.keys():
            authors[link] = authors[link] + 1
        else:
            authors[link] = 1
    for link, number in authors.iteritems():
        '''
        Get inside the teacher's page which contains all the announcements
        '''
        output = teilar_login('http://www.teilar.gr/%s', link)
        soup = BeautifulSoup(output)
        try:
            author_name = soup.find('td', 'BlueTextBold').i.contents[0]
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data(link))
            logger_mail.exception(error)
            raise CronosError(u'Παρουσιάστηκε σφάλμα κατά την ανάκτηση του ονόματος του καθηγητή')
        '''
        Select only the number of announcements we want
        '''
        try:
            announcements_all = soup.find_all('td', 'LineDownDots')[0:number]
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data(link))
            logger_mail.exception(error)
            raise CronosError(u'Παρουσιάστηκε σφάλμα κατά την ανάκτηση του ονόματος του καθηγητή')
        for announcement in announcements_all:
            '''
            Parse data from each announcement
            '''
            try:
                temp_td_blacktext11 = announcement.find_all('td', 'BlackText11')
                title = temp_td_blacktext11[0].b.contents[0]
                pubdate = announcement.find('td', 'OraText').contents[0].split('/')
                pubdate = date(int(pubdate[2]), int(pubdate[1]), int(pubdate[0]))
                description = temp_td_blacktext11[1]
                try:
                    enclosure = feedgenerator.Enclosure(announcement.find('a', 'OraText')['href'], 'Unknown', 'Unknown')
                except Exception as error:
                    enclosure = None
            except Exception as error:
                logger_syslog.error(error, extra = log_extra_data(author_name))
                logger_mail.exception(error)
                raise CronosError(u'Παρουσιάστηκε σφάλμα κατά την ανάκτηση ανακοινώσεων καθηγητή')
            add_rss_item(custom_rss, title, 'http://teilar.gr/' + link, pubdate, description, author_name, enclosure)
    write_rss_file(custom_rss, 'teachers.rss')
    return

if __name__ == '__main__':
    try:
        get_teilar()
        get_teachers()
    except CronosError as error:
        logger_syslog.error(error.value, extra = log_extra_data())
