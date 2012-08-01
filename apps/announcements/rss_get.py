# -*- coding: utf-8 -*-

import os
import sys
from proj_root import PROJECT_ROOT
sys.path.append(PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.settings'
from apps import CronosError, log_extra_data
from apps.teilar.models import Departments
from apps.eclass.models import Lessons
from django.conf import settings
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
        '''
        Remote RSS files
        '''
        u'Γενικές ανακοινώσες openclass.teilar.gr': 'http://openclass.teilar.gr/rss.php',
        u'LinuxTeam ΤΕΙ Λάρισας': 'http://linuxteam.teilar.gr/rss.xml',
        u'Κέντρο Διαχείρισης Δικτύου ΤΕΙ Λάρισας': 'http://noc.teilar.gr/index.php/2012-05-10-08-28-35.feed?type=atom',
        u'Μονάδα Καινοτομίας και Επιχειρηματικότητας': 'http://mke.teilar.gr/business/mathimata-ann.feed',
        u'Πύλη ΑμΕΑ ΤΕΙ Λάρισας': 'http://disabled.teilar.gr/index.php?format=feed&type=rss',
        # PR? It seems to provide RSS, but there are no announcements there yet to check how good it is
        # TODO: cronos!
        # TODO: diogenis!
        '''
        Custom made RSS files
        '''
        u'DC:CREATOR': '%s/%s' % (settings.RSS_PATH, 'teilar.rss'), # Various teilar websites' announcements
        u'DC:CREATOR': '%s/%s' % (settings.RSS_PATH, 'teachers.rss'), # All teachers' announcements
        #u'Τμήμα Διοίκησης και Διαχείρισης έργων': '%s/%s' % (settings.RSS_PATH, 'dde.rss'),
        #u'Γραμματεία ΤΕΙ Λάρισας': '%s/%s' % (settings.RSS_PATH, 'dionysos.rss'),
        #u'Βιβλιοθήκη ΤΕΙ Λάρισας': '%s/%s' % (settings.RSS_PATH, 'library.rss'),
        #u'carrer?': '%s/%s' % (settings.RSS_PATH, 'career.rss'),
        #u'Μονάδα Διασφάλισης Ποιότητας ΤΕΙ Λάρισας': '%s/%s' % (settings.RSS_PATH, 'modip.rss'),
    }

    '''
    Add the eclass lessons in the list of RSS sites
    '''
    try:
        eclass_lessons = Lessons.objects.filter(deprecated = False)
        for lesson in eclass_lessons:
            sites[lesson.name] = 'http://openclass.teilar.gr/modules/announcements/rss.php?c=%s' % lesson.urlid
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

def get_announcements(sites):
    '''
    Parse the RSS feed and grab the tags that are of interest
    '''
    for author, site in sites.iteritems():
        rss = feedparser.parse(site)
        if len(rss.entries) > 10:
            entries = rss.entries[:10][::-1]
        else:
            entries = rss.entries[::-1]
        for entry in entries:
            add_announcement_to_db()
            print '\n\n## entry.title ##'
            print entry.title
            print '## entry.link ##'
            print entry.link
            print '## entry.published ##'
            print entry.published
            print '## entry.published_parsed ##'
            print entry.published_parsed
            print '## entry.updated ##'
            print entry.updated
            print '## entry.updated_parsed ##'
            print entry.updated_parsed
            print '## entry.summary ##'
            print entry.summary
            try:
                print '## entry.author ##'
                print entry.author
            except:
                print '## author ##'
                print author
            try:
                print '## entry.enclosure ##'
                for enclosure in entry.enclosures:
                    print enclosure.href
            except:
                pass

def add_announcement_to_db():
    return

def update_announcements():
    '''
    Update the announcements
    '''
    sites = get_sites()
    get_announcements(sites)
    return

if __name__ == '__main__':
    try:
        update_announcements()
    except CronosError as error:
        logger_syslog.error(error.value, extra = log_extra_data())
