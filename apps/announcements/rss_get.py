# -*- coding: utf-8 -*-

import os
import sys
from proj_root import PROJECT_ROOT
sys.path.append(PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.settings'
from apps import CronosError, log_extra_data
from apps.announcements.models import Announcements
from apps.teilar.models import Departments
from apps.eclass.models import Lessons
from django.conf import settings
from django.db.utils import IntegrityError
from xml.sax._exceptions import SAXException
import MySQLdb
import feedparser
import logging
import urllib2

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

def get_sites():
    '''
    Retrieves the sites that offer RSS, both from local files
    and from the DB
    The sites dictionary has the creator's name as key, and the
    URL or path as value.
    If we want to use the <dc:creator> tag of the RSS instead
    of the creator written in key value, then the creator in the
    key gets the suffix "_dummy"
    '''
    sites = {
        ## Remote RSS files ##
        u'Γενικές ανακοινώσες openclass.teilar.gr': u'http://openclass.teilar.gr/rss.php',
        u'LinuxTeam ΤΕΙ Λάρισας': u'http://linuxteam.teilar.gr/rss.xml',
        u'Κέντρο Διαχείρισης Δικτύου ΤΕΙ Λάρισας': u'http://noc.teilar.gr/index.php/2012-05-10-08-28-35.feed?type=atom',
        u'Μονάδα Καινοτομίας και Επιχειρηματικότητας': u'http://mke.teilar.gr/business/mathimata-ann.feed',
        u'Πύλη ΑμΕΑ ΤΕΙ Λάρισας': u'http://disabled.teilar.gr/index.php?format=feed&type=rss',
        # PR? It seems to provide RSS, but there are no announcements there yet to check how good it is
        # TODO: cronos!
        # TODO: diogenis!
        ## Custom made RSS files ##
        u'Γενικές Ανακοινώσεις': u'%s/%s' % (settings.RSS_PATH, 'general.rss'),
        u'Ανακοινώσεις του ΤΕΙ Λάρισας': u'%s/%s' % (settings.RSS_PATH, 'teilar_ann_dummy.rss'),
        u'Συνεδριάσεις Συμβουλίου ΤΕΙ Λάρισας': u'%s/%s' % (settings.RSS_PATH, 'council.rss'),
        u'Ανακοινώσεις της Επιτροπής Εκπαίδευσης και Ερευνών του ΤΕΙ Λάρισας': u'%s/%s' % (settings.RSS_PATH, 'committee.rss'),
        u'departments_dummy': u'%s/%s' % (settings.RSS_PATH, 'departments.rss'),
        u'teachers_dummy': u'%s/%s' % (settings.RSS_PATH, 'teachers.rss'),
        #u'Τμήμα Διοίκησης και Διαχείρισης έργων': u'%s/%s' % (settings.RSS_PATH, 'dde.rss'),
        #u'Γραμματεία ΤΕΙ Λάρισας': u'%s/%s' % (settings.RSS_PATH, 'dionysos.rss'),
        #u'Βιβλιοθήκη ΤΕΙ Λάρισας': u'%s/%s' % (settings.RSS_PATH, 'library.rss'),
        #u'carrer?': u'%s/%s' % (settings.RSS_PATH, 'career.rss'),
        #u'Μονάδα Διασφάλισης Ποιότητας ΤΕΙ Λάρισας': u'%s/%s' % (settings.RSS_PATH, 'modip.rss'),
    }

    '''
    Add the eclass lessons in the list of RSS sites
    '''
    try:
        eclass_lessons = Lessons.objects.filter(deprecated = False)
        for lesson in eclass_lessons:
            sites[lesson.name] = u'http://openclass.teilar.gr/modules/announcements/rss.php?c=%s' % lesson.urlid
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data())
        logger_mail.exception(error)
        raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με τη βάση δεδομένων')

    '''
    Add the Departments from the DB in the list of RSS sites
    EDIT: They don't offer good RSS, I am recreating it
    '''
    #departments = Departments.objects.filter(deprecated = False)
    #for department in departments:
    #    sites[department.name] = 'http://teilar.gr/tmimata/rss_tmima_news_xml.php?tid=%i' % department.urlid
    return sites

def add_announcement_to_db(announcement):
    '''
    Add the announcement to the DB
    '''
    # TODO: Fix pubdate
    # TODO: create an announcements_authors table that will connect authors from various tables with the announcements table
    try:
        new_announcement = Announcements(
            title = announcement[0],
            link = announcement[1],
            #pubdate = announcement[2],
            pubdate = None,
            summary = announcement[3],
            creator = announcement[4],
            enclosure = announcement[5],
            unique = announcement[6],
        )
        status = u'Νέα ανακοίνωση'
        new_announcement.save()
        logger_syslog.info(status, extra = log_extra_data(announcement[0]))
    except IntegrityError as error:
        if tuple(error)[0] == 1062 and tuple(error)[1].endswith("'unique'"):
            '''
            If the error is a duplicate entry for unique, then silently move forward
            '''
            pass
        else:
            logger_syslog.error(error, extra = log_extra_data(announcement[0]))
            logger_mail.exception(error)
    except MySQLdb.Warning as warning:
        logger_syslog.info(status, extra = log_extra_data(announcement[0]))
        logger_syslog.warning(warning, extra = log_extra_data(announcement[0]))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(announcement[0]))
        logger_mail.exception(error)
    return

def parse_or_fix_rss(site):
    '''
    Parse the RSS feed. If there are problems, try to work around them
    '''
    try:
        rss = feedparser.parse(site)
    except SAXException as warning:
        '''
        Failed to parse the RSS feed, try to fix it
        '''
        logger_syslog.warning(warning, extra = log_extra_data(site))
        '''
        Download the RSS file manually
        '''
        output = urllib2.urlopen(site).read()
        '''
        Clean no-break space
        '''
        output = output.replace('\xa0 ', ' ').replace('\xa0 ', ' ').replace('\xc2 ', '\xc2\xa0 ').replace('\xc2\xa0', '')
        try:
            rss = feedparser.parse(output)
            logger_syslog.info('FIXED!', extra = log_extra_data(site))
        except Exception as error:
            '''
            Still no success, giving up
            '''
            # TODO: Try to grab the <item>s with bs4 and create a custom RSS feed
            logger_syslog.error(error, extra = log_extra_data(site))
            logger_mail.exception(error)
            return None
    return rss

def get_announcement(entry, creator, site):
    '''
    Return a list with the announcement's tags that are of interest
    '''
    title = entry.title
    link = entry.link
    pubdate = entry.updated_parsed
    summary = entry.summary
    '''
    Select either the creator of the RSS or
    the creator from the value of the key of
    the 'sites' dictionary
    '''
    if creator.endswith(u'_dummy'):
        creator = entry.author
    try:
        enclosure = entry.enclosures[0].href
    except:
        enclosure = None
    if site.endswith(u'teachers.rss'):
        '''
        Teachers have all the announcements in a
        single page, instead of having each one
        in its own page, thus the unique field
        has to be combined with something else
        '''
        unique = link + summary
        if enclosure:
            unique += enclosure
    else:
        unique = link
    announcement = [title, link, pubdate, summary, creator, enclosure, unique]
    return announcement

def update_announcements():
    '''
    Update the DB with new announcements of all the websites listed in sites.keys()
    '''
    sites = get_sites()
    for creator, site in sites.iteritems():
        '''
        Try to parse the RSS feed
        In case it is broken, try to fix it as well
        '''
        rss = parse_or_fix_rss(site)
        if not rss:
            '''
            Didn't manage to fix it, give up and move on
            '''
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
            announcement = get_announcement(entry, creator, site)
            add_announcement_to_db(announcement)

if __name__ == '__main__':
    try:
        update_announcements()
    except CronosError as error:
        logger_syslog.error(error.value, extra = log_extra_data())
