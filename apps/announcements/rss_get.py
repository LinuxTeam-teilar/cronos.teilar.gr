# -*- coding: utf-8 -*-

import os
import sys
from proj_root import PROJECT_ROOT
sys.path.append(PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.settings'
from apps.teilar.models import Departments
from apps.eclass.models import Lessons
import feedparser

'''
List of sites that offer RSS
'''
sites = {
    u'Γενικές ανακοινώσες openclass.teilar.gr': 'http://openclass.teilar.gr/rss.php',
    u'LinuxTeam ΤΕΙ Λάρισας': 'http://linuxteam.teilar.gr/rss.xml',
    u'Κέντρο Διαχείρισης Δικτύου ΤΕΙ Λάρισας': 'http://noc.teilar.gr/index.php/2012-05-10-08-28-35.feed?type=atom',
    u'Μονάδα Καινοτομίας και Επιχειρηματικότητας': 'http://mke.teilar.gr/business/mathimata-ann.feed',
    u'Πύλη ΑμΕΑ ΤΕΙ Λάρισας': 'http://disabled.teilar.gr/index.php?format=feed&type=rss',
}

'''
Add the Departments from the DB in the list of RSS sites
EDIT: They don't offer good RSS, I am recreating it
'''
#departments = Departments.objects.filter(deprecated = False)
#for department in departments:
#    sites[department.name] = 'http://teilar.gr/tmimata/rss_tmima_news_xml.php?tid=%i' % department.urlid

'''
Add the eclass lessons in the list of RSS sites
'''
eclass_lessons = Lessons.objects.filter(deprecated = False)
for lesson in eclass_lessons:
    sites[lesson.name] = 'http://openclass.teilar.gr/modules/announcements/rss.php?c=%s' % lesson.urlid

'''
Add the teilar.gr announcements in the list of RSS sites
'''
sites['announcements_teilar'] = '/tmp/announcements_teilar.rss'

for author, site in sites.iteritems():
    rss = feedparser.parse(site)
    if len(rss.entries) > 10:
        entries = rss.entries[:10][::-1]
    else:
        entries = rss.entries[::-1]
    for entry in entries:
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
