# -*- coding: utf-8 -*-

from cronos.announcements.models import Announcements
from cronos.user.models import *
from django.contrib.auth.models import User
from django.contrib.syndication.feeds import *

class AnnouncementFeed(Feed):
    title = 'Ανακοινώσεις ΤΕΙ Λάρισας'
    link = 'http://cronos.teilar.gr'
    description = 'Ανακοινώσεις διαφόρων ιστοσελίδων του ΤΕΙ Λάρισας. Παρέχονται από το http://cronos.teilar.gr'

    def get_object(self, bits):
        return User.objects.get(username = bits[0])

    def items(self, obj):
        all_announcements = []
        all_announcements_ids = [obj.get_profile().school]
        try:
            all_announcements_ids += obj.get_profile().eclass_lessons.split(',')
            all_announcements_ids += obj.get_profile().other_announcements.split(',')
            all_announcements_ids += obj.get_profile().teacher_announcements.split(',')
        except:
            pass
        return Announcements.objects.filter(urlid__urlid__in = all_announcements_ids).order_by('-date_fetched')[:30]

    def item_author_name(self, item):
        return item.author()
