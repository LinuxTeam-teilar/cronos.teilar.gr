# -*- coding: utf-8 -*-

from apps.rss_creator.models import AnnouncementsTeilar
from django.contrib.syndication.views import Feed

class AnnouncementsTeilarFeed(Feed):
    title = 'test'
    link = 'test'
    description = 'test'

    def items(self):
        return AnnouncementsTeilar.objects.all()[:30]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description
