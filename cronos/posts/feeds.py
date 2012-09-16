# -*- coding: utf-8 -*-

from cronos.posts.views import get_posts
from django.contrib.auth.models import User
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
import mimetypes

class PostsFeed(Feed):
    link = 'http://cronos.teilar.gr'

    def get_object(self, request, username, page):
        if page == u'announcements':
            user = get_object_or_404(User, username=username)
        else:
            user = None
        return [user, page]

    def title(self, obj):
        page = obj[1]
        if page == u'announcements':
            return 'Ανακοινώσεις TEI Λάρισας από το cronos.teilar.gr'
        elif page == u'blog':
            return 'Blog cronos.teilar.gr'

    def description(self, obj):
        page = obj[1]
        if page == u'announcements':
            return 'Ανακοινώσεις επιλεγμένων ιστοσελίδων του ΤΕΙ Λάρισας. Παρέχονται από το http://cronos.teilar.gr'
        elif page == u'blog':
            return 'Blog posts του http://cronos.teilar.gr'

    def items(self, obj):
        user = obj[0]
        page = obj[1]
        posts = get_posts(user, None, page)
        title = posts.pop()
        return posts

    def item_title(self, item):
        return item.title

    def item_link(self, item):
        return u'http://cronos.teilar.gr/posts/' + str(item.id)

    def item_author_name(self, item):
        return item.creator

    def item_author_link(self, item):
        return item.creator_url

    def item_author_email(self, item):
        return item.creator.content_object.email

    def item_pubdate(self, item):
        return item.pubdate

    def item_description(self, item):
        return item.summary

    def item_enclosure_url(self, item):
        return item.enclosure

    def item_enclosure_mime_type(self, item):
        try:
            mimetypes.init()
            extension = '.' + item.enclosure.split('.')[-1]
            enclosure_mimetype = mimetypes.types_map[extension]
        except:
            enclosure_mimetype = None
        return enclosure_mimetype

    def item_enclosure_length(self):
        return
