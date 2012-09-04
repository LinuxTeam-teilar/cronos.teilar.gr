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
        Find the creator
        '''
        model_name = str(announcement.creator.content_type.name)
        creator = eval(model_name).objects.get(pk=announcement.creator.object_id)
        announcement = announcement.__dict__
        '''
        Change the creator's attributes to the related ones
        '''
        announcement['creator'] = creator.name
        announcement['creator_url'] = creator.url.split('::')[0]
        if creator.email:
            announcement['creator_email'] = creator.email
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
            request.user.get_profile().eclass_lessons,
            request.user.get_profile().teacher_announcements,
            request.user.get_profile().other_announcements,
        ]
        for list_of_authors in following_meta_authors:
            for author in list_of_authors.all():
                following_authors.append(author)
        '''
        Add the school in the following authors as well
        '''
        following_authors.append(request.user.get_profile().school)
        for author in following_authors:
            '''
            Find the creator
            '''
            author_type = ContentType.objects.get_for_model(author)
            creator = Authors.objects.get(content_type__pk = author_type.id, object_id = author.id)
            for announcement in Announcements.objects.filter(creator = creator).order_by('-pubdate')[:100]:
                announcement = announcement.__dict__
                '''
                Change the creator's attributes to the related values
                '''
                announcement['creator'] = author.name
                announcement['creator_url'] = author.url.split('::')[0]
                if author.email:
                    announcement['creator_email'] = author.email
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
