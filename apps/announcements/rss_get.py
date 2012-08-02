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
import MySQLdb
import feedparser
import logging

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

def get_sites():
    '''
    Retrieves the sites that offer RSS, both from local files
    and from the DB
    The sites dictionary has the author's name as key, and the
    URL or path as value.
    If we want to use the <dc:creator> tag of the RSS instead
    of the author written in key value, then the author in the
    key gets the dummy name "DC:CREATOR"
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
        u'teilar_dummy': u'%s/%s' % (settings.RSS_PATH, 'teilar.rss'), # Various teilar websites' announcements
        u'teachers_dummy': u'%s/%s' % (settings.RSS_PATH, 'teachers.rss'), # All teachers' announcements
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

def get_announcements():
    '''
    Get the announcements and add them to the DB
    '''
    sites = get_sites()

    '''
    Parse the RSS feed and grab the tags that are of interest
    '''
    for author, site in sites.iteritems():
        print '\n\n######'
        print author
        print site
        rss = feedparser.parse(site)
        if len(rss.entries) > 10:
            entries = rss.entries[:10][::-1]
        else:
            entries = rss.entries[::-1]
        for entry in entries:
            title = entry.title
            link = entry.link
            pubdate = entry.updated_parsed
            summary = entry.summary
            if author.endswith(u'_dummy'):
                author = entry.author
            try:
                enclosure = entry.enclosures[0].href
            except:
                enclosure = None
            if site.endswith(u'teachers.rss'):
                unique = link + summary
                if enclosure:
                    unique += enclosure
            else:
                unique = link
            announcement = [title, link, pubdate, summary, author, enclosure, unique]
            add_announcement_to_db(announcement)

def add_announcement_to_db(announcement):
    '''
    Add the announcement to the DB
    '''
    # TODO: check first that the announcement is not there using the "unique field"
    # TODO: Fix pubdate
    # TODO: create an announcements_authors table that will connect authors from various tables with the announcements table
    try:
        new_announcement = Announcements(
            title = announcement[0],
            link = announcement[1],
            #pubdate = announcement[2],
            pubdate = None,
            summary = announcement[3],
            author = announcement[4],
            enclosure = announcement[5],
            unique = announcement[6],
        )
        status = u'Νέα ανακοίνωση'
        new_announcement.save()
        logger_syslog.info(status, extra = log_extra_data(cronjob = announcement[0]))
    except MySQLdb.Warning as warning:
        logger_syslog.info(status, extra = log_extra_data(cronjob = announcement[0]))
        logger_syslog.warning(warning, extra = log_extra_data(cronjob = announcement[0]))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(cronjob = announcement[0]))
        logger_mail.exception(error)
        raise CronosError(u'Παρουσιάστηκε σφάλμα κατά την προσθήκη ανακοίνωσης στη βάση δεδομένων')
    return

if __name__ == '__main__':
    try:
        get_announcements()
    except CronosError as error:
        logger_syslog.error(error.value, extra = log_extra_data())
