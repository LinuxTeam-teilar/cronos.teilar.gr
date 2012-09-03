# -*- coding: utf-8 -*-

from cronos.common.log import CronosError, log_extra_data
from cronos.announcements.models import Authors
from cronos.teilar.models import Websites
from django.conf import settings
from django.core.management.base import BaseCommand
import logging

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

class Command(BaseCommand):
    def get_websites(self):
        '''
        Retrieves RSS feeds either from remote sites from local files or
        from the DB
        The entries in the dictionary are in the following structure:
        {'url': ['name', 'rss', 'email']}
        If we want to use the <dc:creator> tag of the RSS instead
        of the creator written in key value, then the creator in the
        key gets the suffix "_dummy"
        '''
        websites = {
            u'http://openclass.teilar.gr': [
                u'http://openclass.teilar.gr/rss.php',
                u'Γενικές ανακοινώσεις openclass.teilar.gr',
                None,
            ],
            u'http://linuxteam.teilar.gr': [
                u'LinuxTeam ΤΕΙ Λάρισας',
                u'http://linuxteam.teilar.gr/rss.xml',
                u'linuxteam@teilar.gr',
            ],
            u'http://noc.teilar.gr': [
                u'Κέντρο Διαχείρισης Δικτύου ΤΕΙ Λάρισας',
                u'http://noc.teilar.gr/index.php/2012-05-10-08-28-35.feed?type=atom',
                u'noc@teilar.gr',
            ],
            u'http://mke.teilar.gr': [
                u'Μονάδα Καινοτομίας και Επιχειρηματικότητας',
                u'http://mke.teilar.gr/business/mathimata-ann.feed',
                u'mke@teilar.gr',
            ],
            u'http://disabled.teilar.gr': [
                u'Πύλη ΑμΕΑ ΤΕΙ Λάρισας',
                u'http://disabled.teilar.gr/index.php?format=feed&type=rss',
                None,
            ],
            u'http://diogenis.teilar.gr': [
                u'Ηλεκτρονική εγγραφή εργαστηρίων',
                u'https://www.facebook.com/feeds/page.php?format=atom10&id=153439198094399',
                u'diogenis@teilar.gr',
            ],
            u'http://cronos.teilar.gr': [
                u'Υπηρεσία ενοποίησης πληροφοριών',
                u'http://linuxteam.teilar.gr/blog/1464/feed',
                u'cronos@teilar.gr',
            ],
            #u'http://www.pr.teilar.gr': [
            #    u'Γραφείο Δημοσίων & Διεθνών Σχέσεων',
            #    u'http://www.pr.teilar.gr/TODO',
            #    u'pr@teilar.gr',
            #],
            ## Custom made RSS files ##
            u'http://www.teilar.gr::general': [
                u'Γενικές Ανακοινώσεις',
                u'%s/%s' % (settings.RSS_PATH, 'general.rss'),
                None,
            ],
            u'http://www.teilar.gr::teilar_ann': [
                u'Ανακοινώσεις του ΤΕΙ Λάρισας',
                u'%s/%s' % (settings.RSS_PATH, 'teilar_ann.rss'),
                None,
            ],
            u'http://www.teilar.gr::council': [
                u'Συνεδριάσεις Συμβουλίου ΤΕΙ Λάρισας',
                u'%s/%s' % (settings.RSS_PATH, 'council.rss'),
                None,
            ],
            u'http://www.teilar.gr::committee': [
                u'Ανακοινώσεις της Επιτροπής Εκπαίδευσης και Ερευνών του ΤΕΙ Λάρισας',
                u'%s/%s' % (settings.RSS_PATH, 'committee.rss'),
                None,
            ],
            u'departments_dummy': [
                u'departments_dummy',
                u'%s/%s' % (settings.RSS_PATH, 'departments.rss'),
                None,
            ],
            u'teachers_dummy': [
                u'teachers_dummy',
                u'%s/%s' % (settings.RSS_PATH, 'teachers.rss'),
                u'teachers_dummy',
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

    def add_website_to_db(self, url, attributes):
        '''
        Add the website to the DB
        '''
        name = attributes[0]
        rss = attributes[1]
        email = attributes[2]
        website = Websites(
            url = url,
            name = name,
            rss = rss,
            email = email,
        )
        try:
            website.save()
            logger_syslog.info(u'Επιτυχής προσθήκη', extra = log_extra_data(url))
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data(url))
            logger_mail.exception(error)
            return
        author = Authors(content_object = website)
        try:
            author.save()
            logger_syslog.info(u'Επιτυχής προσθήκη', extra = log_extra_data(url))
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data(url))
            logger_mail.exception(error)
        return

    def deprecate_website_in_db(self, url, websites_from_db_q):
        '''
        Mark websites as inactive
        '''
        website = websites_from_db_q.get(url = url)
        website.is_active = False
        try:
            website.save()
            logger_syslog.info(u'Αλλαγή κατάστασης σε inactive', extra = log_extra_data(url))
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data(url))
            logger_mail.exception(error)
        return

    def update_websites(self):
        '''
        1) Find websites that were removed and mark them as inactive
        2) Find new websites and add them
        3) In the existing websites, find changes in their attributes and
        update them accordingly
        '''
        websites = self.get_websites()
        '''
        Get all the websites from the DB and put them in a dictionary in the structure:
        websites_from_db = {'url': ['name', 'rss', 'email']}
        '''
        websites_from_db = {}
        try:
            websites_from_db_q = Websites.objects.filter(is_active = True)
            for website in websites_from_db_q:
                websites_from_db[website.url] = [website.name, website.rss, website.email]
        except Exception as error:
           logger_syslog.error(error, extra = log_extra_data())
           logger_mail.exception(error)
           raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με τη βάση δεδομένων')
        '''
        Get the websites' URLs in set data structure, for easier comparisons
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
        Get ex websites and mark them as inactive
        '''
        ex_websites = websites_from_db_set - websites_from_teilar_set
        for url in ex_websites:
            self.deprecate_website_in_db(url, websites_from_db_q)
        '''
        Get new websites and add them to the DB
        '''
        new_websites = websites_from_teilar_set - websites_from_db_set
        for url in new_websites:
           self.add_website_to_db(url, websites[url])
        '''
        Get all the existing websites, and check if any of their attributes were updated
        '''
        existing_websites = websites_from_teilar_set & websites_from_db_set
        for url in existing_websites:
            i = 0
            website = websites_from_db_q.get(url = url)
            for attribute in websites[url]:
                if websites_from_db[url][i] != attribute:
                    if i == 0:
                        attr_name = u'name'
                        website.name = attribute
                    elif i == 1:
                        attr_name = u'rss'
                        website.url = attribute
                    elif i == 2:
                        attr_name = u'email'
                        website.email = attribute
                    try:
                        website.save()
                        status = u'Επιτυχής ανανέωση του %s σε %s' % (attr_name, attribute)
                        logger_syslog.info(status, extra = log_extra_data(url))
                    except Exception as error:
                        logger_syslog.error(error, extra = log_extra_data(url))
                        logger_mail.exception(error)
                i += 1
        return

    def handle(self, *args, **options):
        self.update_websites()
