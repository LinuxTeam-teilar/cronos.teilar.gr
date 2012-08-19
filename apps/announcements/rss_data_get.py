# -*- coding: utf-8 -*-

import os
import sys
from proj_root import PROJECT_ROOT
sys.path.append(PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.settings'
from apps import CronosError, log_extra_data
from apps.announcements.models import Authors, Announcements
from apps.teilar.models import Departments, Websites
from apps.eclass.models import Lessons
from django.conf import settings
from django.db.utils import IntegrityError
from django.utils import timezone
from time import mktime
from xml.sax._exceptions import SAXException
import datetime
import MySQLdb
import feedparser
import logging
import urllib2

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

def get_authors():
    '''
    Retrieves the authors from the DB tables:
    Departments, Teachers, Lessons, Websites
    '''
    authors = {}
    try:
        websites = Websites.objects.filter(deprecated = False)
        for website in websites:
            authors[website.rss] = website.name
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data())
        logger_mail.exception(error)
        raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με τη βάση δεδομένων')
    '''
    Add the eclass lessons in the list of RSS sites
    '''
    try:
        eclass_lessons = Lessons.objects.filter(deprecated = False)
        for lesson in eclass_lessons:
            authors[u'http://openclass.teilar.gr/modules/announcements/rss.php?c=%s' % lesson.url.split('/')[4]] = lesson.name
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data())
        logger_mail.exception(error)
        raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με τη βάση δεδομένων')
    '''
    Add the Departments from the DB in the list of RSS sites
    EDIT: They don't offer good RSS, I am recreating it, it is included in Websites table
    '''
    #departments = Departments.objects.filter(deprecated = False)
    #for department in departments:
    #    authors['http://teilar.gr/tmimata/rss_tmima_news_xml.php?tid=%i' % department.url.split('=')[1] = department.name
    return authors

def add_announcement_to_db(announcement):
    '''
    Add the announcement to the DB
    '''
    try:
        '''
        Get a creator object from the Authors table
        '''
        for item in Authors.objects.all():
            if item.content_object.name == announcement[4]:
                creator = item
                break
        new_announcement = Announcements(
            title = announcement[0],
            url = announcement[1],
            pubdate = announcement[2],
            summary = announcement[3],
            creator = creator,
            enclosure = announcement[5],
            unique = announcement[6],
        )
        status = u'Νέα ανακοίνωση'
        new_announcement.save()
        logger_syslog.info(status, extra = log_extra_data(announcement[1]))
    except IntegrityError as error:
        if tuple(error)[0] == 1062 and tuple(error)[1].endswith("'unique'"):
            '''
            If the error is a duplicate entry for unique, then silently move forward
            '''
            pass
        else:
            logger_syslog.error(error, extra = log_extra_data(announcement[1]))
            logger_mail.exception(error)
    except MySQLdb.Warning as warning:
        logger_syslog.info(status, extra = log_extra_data(announcement[1]))
        logger_syslog.warning(warning, extra = log_extra_data(announcement[1]))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(announcement[1]))
        logger_mail.exception(error)
    return

def get_announcement(creator, entry, rss_url):
    '''
    Return a list with the announcement's tags that are of interest
    '''
    title = entry.title
    url = entry.link
    try:
        pubdate = entry.updated_parsed
        pubdate = datetime.datetime.fromtimestamp(mktime(entry.updated_parsed))
    except AttributeError as error:
        pubdate = datetime.datetime.now()
    pubdate = timezone.make_aware(pubdate, timezone.get_default_timezone())
    summary = entry.summary
    '''
    Select either the creator of the RSS or
    the creator from the value of the key of
    the 'authors' dictionary
    '''
    if creator.endswith(u'_dummy'):
        creator = entry.author
    try:
        enclosure = entry.enclosures[0].href
    except:
        enclosure = None
    unique = url
    if rss_url.endswith(u'teachers.rss'):
        '''
        Teachers have all the announcements in a
        single page, instead of having each one
        in its own page, thus the unique field
        has to be combined with something else
        '''
        unique += summary
        if enclosure:
            unique += enclosure
    announcement = [title, url, pubdate, summary, creator, enclosure, unique]
    return announcement

def update_announcements():
    '''
    Update the DB with new announcements of all the websites listed in authors.keys()
    '''
    authors = get_authors()
    for rss_url, creator in authors.iteritems():
        '''
        Parse the RSS feed
        '''
        try:
            rss = feedparser.parse(rss_url)
        except Exception as error:
            '''
            Something went wrong, skip it and go to the next one
            '''
            logger_syslog.error(error, extra = log_extra_data(rss_url))
            logger_mail.exception(error)
            continue
        '''
        Grab the latest max 10 announcements
        '''
        if len(rss.entries) > 10:
            entries = rss.entries[:10][::-1]
        else:
            entries = rss.entries[::-1]
        for entry in entries:
            '''
            Get the data of each entry and add them in DB
            '''
            announcement = get_announcement(creator, entry, rss_url)
            add_announcement_to_db(announcement)

if __name__ == '__main__':
    try:
        update_announcements()
    except CronosError as error:
        logger_syslog.error(error.value, extra = log_extra_data())
