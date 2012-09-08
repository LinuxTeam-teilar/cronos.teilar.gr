# -*- coding: utf-8 -*-

from cronos.announcements.models import Authors, Announcements
from cronos.announcements.forms import PostForm
from cronos.teilar.models import Departments as departments
from cronos.teilar.models import Teachers as teachers
from cronos.teilar.models import Websites as websites
from cronos.teilar.models import EclassLessons as eclasslessons
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response
from django.template import RequestContext

def get_creator(announcement, creator):
    '''
    Add creator's name, URL, mail and avatar in the announcement dict
    '''
    announcement.creator_url = creator.url.split('::')[0]
    if creator.email:
        announcement.creator_email = creator.email
    '''
    Get the avatar based on the url
    '''
    announcement.avatar = u'img/avatar_%s.png' % creator.url.split('/')[2]
    try:
        url = creator.url.split('/')[3]
        if url == u'tmimata':
            announcement.avatar = u'img/avatar_department.png'
        elif url.split('?')[0] == u'person.php':
            if url.split('=')[1] == u'323':
                announcement.avatar = u'img/avatar_calendar.png'
            elif url.split('=')[1] == u'324':
                announcement.avatar = u'img/avatar_news.png'
            else:
                announcement.avatar = u'img/avatar_teacher.png'
    except:
        pass
    try:
        url = creator.url.split('::')[1]
        if url == u'teilar_ann' or url == u'general':
            announcement.avatar = u'img/avatar_www.teilar.gr.png'
        else:
            announcement.avatar = u'img/avatar_%s.png' % url
    except:
        pass
    return announcement

@login_required
def announcements(request):
    '''
    Prints announcements
    '''
    announcements = []
    if request.GET.get('post_id'):
        form = PostForm(request.POST)
        '''
        If the post ID is passed in the hidden form, only
        this post will be shown
        '''
        post_id = request.GET.get('post_id')
        announcement = Announcements.objects.get(pk=post_id)
        '''
        Add creator's URL, mail and avatar in the announcement
        '''
        announcement = get_creator(announcement, announcement.creator.content_object)
        announcements.append(announcement)
    else:
        form = PostForm()
        following_authors = []
        '''
        The following list has ManyToMany fields from UserProfile. In order
        to get each one of the authors that are included there, we need to
        iterate first the following_meta_authors list, and then iterate each
        one of their contents.
        '''
        following_meta_authors = [
            request.user.get_profile().following_eclass_lessons,
            request.user.get_profile().following_teachers,
            request.user.get_profile().following_websites,
            request.user.get_profile().following_blogs,
        ]
        for list_of_authors in following_meta_authors:
            for author in list_of_authors.all():
                following_authors.append(author)
        '''
        Add the school in the following authors as well
        '''
        following_authors.append(request.user.get_profile().school)
        '''
        Find the creator and put them all in a list, so we can retrieve
        all of their announcements from a query
        '''
        creators = []
        for author in following_authors:
            author_type = ContentType.objects.get_for_model(author)
            creator = Authors.objects.get(content_type__pk = author_type.id, object_id = author.id)
            creators.append(creator)
        '''
        Get all the announcements
        '''
        announcements_q = Announcements.objects.filter(creator__in = creators).order_by('-pubdate')
        for announcement in announcements_q:
            '''
            Add creator's URL, mail and avatar in the announcement dict
            '''
            announcement = get_creator(announcement, announcement.creator.content_object)
            '''
            Add the announcement in the list of the wanted announcements
            '''
            announcements.append(announcement)
    return render_to_response('posts.html', {
            'posts': announcements,
            'form': form,
            'target': 'announcements',
            'tab': 'Ανακοινώσεις',
        }, context_instance = RequestContext(request))
