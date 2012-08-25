# -*- coding: utf-8 -*-

import os
import sys
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__)) + '/../..'
sys.path.append(PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'apps.settings'
from apps import CronosError, log_extra_data
from apps.announcements.models import Authors
from apps.teilar.models import Websites
from django.conf import settings
import logging

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

def get_websites():
    '''
    Retrieves RSS feeds either from remote sites from local files or
    from the DB
    The entries in the dictionary are in the following structure:
    {'rss': ['name', 'url', 'email']}
    If we want to use the <dc:creator> tag of the RSS instead
    of the creator written in key value, then the creator in the
    key gets the suffix "_dummy"
    '''
    websites = {
        u'http://openclass.teilar.gr/rss.php': [
            u'Γενικές ανακοινώσεις openclass.teilar.gr',
            u'http://openclass.teilar.gr',
            None,
        ],
        u'http://linuxteam.teilar.gr/rss.xml': [
            u'LinuxTeam ΤΕΙ Λάρισας',
            u'http://linuxteam.teilar.gr',
            u'linuxteam@teilar.gr',
        ],
        u'http://noc.teilar.gr/index.php/2012-05-10-08-28-35.feed?type=atom': [
            u'Κέντρο Διαχείρισης Δικτύου ΤΕΙ Λάρισας',
            u'http://noc.teilar.gr',
            u'noc@teilar.gr',
        ],
        u'http://mke.teilar.gr/business/mathimata-ann.feed': [
            u'Μονάδα Καινοτομίας και Επιχειρηματικότητας',
            u'http://mke.teilar.gr',
            u'mke@teilar.gr',
        ],
        u'http://disabled.teilar.gr/index.php?format=feed&type=rss': [
            u'Πύλη ΑμΕΑ ΤΕΙ Λάρισας',
            u'http://disabled.teilar.gr',
            None,
        ],
        u'https://www.facebook.com/feeds/page.php?format=atom10&id=153439198094399': [
            u'Ηλεκτρονική εγγραφή εργαστηρίων',
            u'http://diogenis.teilar.gr',
            u'diogenis@teilar.gr',
        ],
        u'http://linuxteam.teilar.gr/blog/1464/feed': [
            u'Υπηρεσία ενοποίησης πληροφοριών',
            u'http://cronos.teilar.gr',
            u'cronos@teilar.gr',
        ],
        #u'http://www.pr.teilar.gr/TODO': [
        #    u'Γραφείο Δημοσίων & Διεθνών Σχέσεων',
        #    u'http://www.pr.teilar.gr',
        #    u'pr@teilar.gr',
        #],
        ## Custom made RSS files ##
        u'%s/%s' % (settings.RSS_PATH, 'general.rss'): [
            u'Γενικές Ανακοινώσεις',
            u'http://www.teilar.gr',
            None,
        ],
        u'%s/%s' % (settings.RSS_PATH, 'teilar_ann_dummy.rss'): [
            u'Ανακοινώσεις του ΤΕΙ Λάρισας',
            u'http://www.teilar.gr',
            None,
        ],
        u'%s/%s' % (settings.RSS_PATH, 'council.rss'): [
            u'Συνεδριάσεις Συμβουλίου ΤΕΙ Λάρισας',
            u'http://www.teilar.gr',
            None,
        ],
        u'%s/%s' % (settings.RSS_PATH, 'committee.rss'): [
            u'Ανακοινώσεις της Επιτροπής Εκπαίδευσης και Ερευνών του ΤΕΙ Λάρισας',
            u'http://www.teilar.gr',
            None,
        ],
        u'%s/%s' % (settings.RSS_PATH, 'departments.rss'): [
            u'departments_dummy',
            u'link_dummy',
            None,
        ],
        u'%s/%s' % (settings.RSS_PATH, 'teachers.rss'): [
            u'teachers_dummy',
            u'link_dummy',
            u'email_dummy',
        ],
        #u'%s/%s' % (settings.RSS_PATH, 'dionysos.rss'): [
        #    u'Γραμματεία ΤΕΙ Λάρισας',
        #    u'http://dionysos.teilar.gr',
        #    u'dionysos@teilar.gr',
        #],
        #u'%s/%s' % (settings.RSS_PATH, 'library.rss'): [
        #    u'Βιβλιοθήκη ΤΕΙ Λάρισας',
        #    u'http://library.teilar.gr',
        #    u'library@teilar.gr',
        #],
        #u'%s/%s' % (settings.RSS_PATH, 'modip.rss'): [
        #    u'Μονάδα Διασφάλισης Ποιότητας ΤΕΙ Λάρισας',
        #    u'http://modip.teilar.gr',
        #    u'info-modip.teilar.gr',
        #],
        #u'%s/%s' % (settings.RSS_PATH, 'career.rss'): [
        #    u'TODO: career',
        #    u'http://www.career.teilar.gr',
        #    u'career@teilar.gr',
        #],
    }
    return websites

def add_website_to_db(rss, attributes):
    '''
    Add the website to the DB
    '''
    name = attributes[0]
    url = attributes[1]
    email = attributes[2]
    website = Websites(
        rss = rss,
        name = name,
        url = url,
        email = email,
    )
    try:
        website.save()
        logger_syslog.info(u'Επιτυχής προσθήκη', extra = log_extra_data(rss))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(rss))
        logger_mail.exception(error)
        return
    author = Authors(content_object = website)
    try:
        author.save()
        logger_syslog.info(u'Επιτυχής προσθήκη', extra = log_extra_data(rss))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(rss))
        logger_mail.exception(error)
    return

def deprecate_website_in_db(rss, websites_from_db_q):
    '''
    Mark websites as deprecated
    '''
    website = websites_from_db_q.get(rss = rss)
    website.deprecated = True
    try:
        website.save()
        logger_syslog.info(u'Αλλαγή κατάστασης σε deprecated', extra = log_extra_data(rss))
    except Exception as error:
        logger_syslog.error(error, extra = log_extra_data(rss))
        logger_mail.exception(error)
    return

def update_websites():
    '''
    1) Find websites that were removed and mark them as deprecated
    2) Find new websites and add them
    3) In the existing websites, find changes in their attributes and
    update them accordingly
    '''
    websites = get_websites()
    '''
    Get all the websites from the DB and put them in a dictionary in the structure:
    websites_from_db = {'rss': ['name', 'url', 'email']}
    '''
    websites_from_db = {}
    try:
        websites_from_db_q = Websites.objects.filter(deprecated = False)
        for website in websites_from_db_q:
            websites_from_db[website.rss] = [website.name, website.url, website.email]
    except Exception as error:
       logger_syslog.error(error, extra = log_extra_data())
       logger_mail.exception(error)
       raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με τη βάση δεδομένων')
    '''
    Get the websites' RSS URLs in set data structure, for easier comparisons
    '''
    websites_from_teilar_set = set(websites.keys())
    try:
        websites_from_db_set = set(websites_from_db.keys())
    except AttributeError:
        '''
        Websites table is empty in the DB
        '''
        websites_from_db_set = set()
    '''
    Get ex websites and mark them as deprecated
    '''
    ex_websites = websites_from_db_set - websites_from_teilar_set
    for rss in ex_websites:
        deprecate_website_in_db(rss)
    '''
    Get new websites and add them to the DB
    '''
    new_websites = websites_from_teilar_set - websites_from_db_set
    for rss in new_websites:
       add_website_to_db(rss, websites[rss])
    '''
    Get all the existing websites, and check if any of their attributes were updated
    '''
    existing_websites = websites_from_teilar_set & websites_from_db_set
    for rss in existing_websites:
        i = 0
        website = websites_from_db_q.get(rss = rss)
        for attribute in websites[rss]:
            if websites_from_db[rss][i] != attribute:
                if i == 0:
                    attr_name = u'name'
                    website.name = attribute
                elif i == 1:
                    attr_name = u'url'
                    website.url = attribute
                elif i == 2:
                    attr_name = u'email'
                    website.email = attribute
                try:
                    website.save()
                    status = u'Επιτυχής ανανέωση του %s σε %s' % (attr_name, attribute)
                    logger_syslog.info(status, extra = log_extra_data(rss))
                except Exception as error:
                    logger_syslog.error(error, extra = log_extra_data(rss))
                    logger_mail.exception(error)
            i += 1
    return

if __name__ == '__main__':
    try:
        update_websites()
    except CronosError as error:
        logger_syslog.error(error.value, extra = log_extra_data())
