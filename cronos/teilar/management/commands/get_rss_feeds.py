# -*- coding: utf-8 -*-

from cronos.common.exceptions import CronosError
from cronos.common.log import log_extra_data
from cronos.posts.models import Authors, Posts
from cronos.teilar.models import Departments, Teachers, Websites, EclassLessons
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import MultipleObjectsReturned
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from django.utils import timezone
from time import mktime
import datetime
import MySQLdb
import feedparser
import logging
import warnings

logger_syslog = logging.getLogger('cronos')
logger_mail = logging.getLogger('mail_cronos')

'''
Convert MySQL warnings to exceptions
'''
warnings.filterwarnings("error", category=MySQLdb.Warning)

class Command(BaseCommand):
    def get_authors(self):
        '''
        Retrieves the authors from the DB tables:
        Departments, Teachers, EclassLessons, Websites
        It returns a dictionary with the following structure:
        authors = {'rss': 'url'}
        (depending on what of those two is unique in each table)
        '''
        authors = {}
        '''
        Add the teilar.gr various websites. It also includes some
        recreated RSS feeds, since the ones that teilar provides are not good
        '''
        try:
            websites = Websites.objects.filter(is_active = True)
            for website in websites:
                authors[website.rss] = website.url
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data())
            logger_mail.exception(error)
            raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με τη βάση δεδομένων')
        '''
        Add the eclass lessons in the list of RSS authors
        '''
        try:
            eclass_lessons = EclassLessons.objects.filter(is_active = True)
            for lesson in eclass_lessons:
                authors[u'http://openclass.teilar.gr/modules/announcements/rss.php?c=%s' % lesson.url.split('/')[4]] = lesson.url
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data())
            logger_mail.exception(error)
            raise CronosError(u'Παρουσιάστηκε σφάλμα σύνδεσης με τη βάση δεδομένων')
        '''
        Add the Departments from the DB in the list of RSS sites
        EDIT: They don't offer good RSS, I am recreating it, it is included in Websites table
        '''
        #departments = Departments.objects.filter(is_active = True)
        #for department in departments:
        #    authors['http://teilar.gr/tmimata/rss_tmima_news_xml.php?tid=%i' % department.url.split('=')[1] = department.url
        return authors

    def add_post_to_db(self, post, unique_url):
        '''
        Add the post to the DB
        '''
        if post[6]:
            '''
            Try to get the author of the post
            If there is post[6] (which means that
            there is dc:creator) then the author should be
            retrieved from the Teachers or Departments table
            '''
            if post[1].split('/')[3].startswith('person'):
                '''
                Since there are teachers with the same name,
                we need to get the author from the URL
                '''
                post[1] = post[1].replace('teilar', 'www.teilar').replace('_announce', '')
                author = Teachers.objects.get(url = post[1])
            else:
                author = Departments.objects.get(name = post[6])
        else:
            for model in [EclassLessons, Websites]:
                try:
                    author = model.objects.get(url = unique_url)
                    break
                except:
                    continue
        '''
        Below are the necessary db relations between the above model
        and the Authors table
        '''
        author_type = ContentType.objects.get_for_model(author)
        creator = Authors.objects.get(content_type__pk = author_type.id, object_id = author.id)
        new_post = Posts(
                title = post[0],
                url = post[1],
                pubdate = post[2],
                summary = post[3],
                creator = creator,
                enclosure = post[4],
                unique = post[5],
        )
        try:
            status = u'Νέα ανακοίνωση'
            new_post.save()
            logger_syslog.info(status, extra = log_extra_data(post[1]))
        except IntegrityError as error:
            if tuple(error)[0] == 1062 and tuple(error)[1].endswith("'unique'"):
                '''
                If the error is a duplicate entry for unique, then silently move forward
                '''
                pass
            else:
                logger_syslog.error(error, extra = log_extra_data(post[1]))
                logger_mail.exception(error)
        except MySQLdb.Warning as warning:
            logger_syslog.info(status, extra = log_extra_data(post[1]))
            logger_syslog.warning(warning, extra = log_extra_data(post[1]))
            if str(warning).startswith("Data truncated for column 'unique' at row"):
                '''
                If the warning is about truncated unique column, ignore it
                '''
                pass
            else:
                logger_mail.exception(warning)
        except Exception as error:
            logger_syslog.error(error, extra = log_extra_data(post[1]))
            logger_mail.exception(error)
        return

    def get_post(self, entry, rss, creator_url):
        '''
        Return a list with the post's tags that are of interest
        '''
        if creator_url.endswith(u'::facebook'):
            title = u'(χωρίς τίτλο)'
        else:
            title = entry.title
        url = entry.link
        try:
            pubdate = entry.updated_parsed
            pubdate = datetime.datetime.fromtimestamp(mktime(entry.updated_parsed))
        except AttributeError as error:
            pubdate = datetime.datetime.now()
        pubdate = timezone.make_aware(pubdate, timezone.get_default_timezone())
        summary = entry.summary
        try:
            enclosure = entry.enclosures[0].href
        except:
            enclosure = None
        unique = url
        if rss.endswith(u'teachers.rss'):
            '''
            Teachers have all the posts in a
            single page, instead of having each one
            in its own page, thus the unique field
            has to be combined with something else
            '''
            unique += summary
            if enclosure:
                unique += enclosure
        creator = None
        if creator_url.endswith(u'_dummy'):
            creator = entry.author
        post = [title, url, pubdate, summary, enclosure, unique, creator]
        return post

    def update_posts(self):
        '''
        Update the DB with new posts of all the websites listed in authors.keys()
        '''
        authors = self.get_authors()
        for rss_url, url in authors.iteritems():
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
            Grab the latest max 10 posts
            '''
            if len(rss.entries) > 10:
                entries = rss.entries[:10][::-1]
            else:
                entries = rss.entries[::-1]
            for entry in entries:
                '''
                Get the data of each entry and add them in DB
                '''
                post = self.get_post(entry, rss_url, url)
                self.add_post_to_db(post, url)

    def handle(self, *args, **options):
        self.update_posts()
