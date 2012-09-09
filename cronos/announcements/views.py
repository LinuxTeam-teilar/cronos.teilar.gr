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

def get_creator(post, creator):
    '''
    Add creator's name, URL, mail and avatar in the post dict
    '''
    post.creator_url = creator.url.split('::')[0]
    if creator.email:
        post.creator_email = creator.email
    '''
    Get the avatar based on the url
    '''
    post.avatar = u'img/avatar_%s.png' % creator.url.split('/')[2]
    try:
        url = creator.url.split('/')[3]
        if url == u'tmimata':
            post.avatar = u'img/avatar_department.png'
        elif url.split('?')[0] == u'person.php':
            if url.split('=')[1] == u'323':
                post.avatar = u'img/avatar_calendar.png'
            elif url.split('=')[1] == u'324':
                post.avatar = u'img/avatar_news.png'
            else:
                post.avatar = u'img/avatar_teacher.png'
    except:
        pass
    try:
        url = creator.url.split('::')[1]
        if url == u'teilar_ann' or url == u'general':
            post.avatar = u'img/avatar_www.teilar.gr.png'
        else:
            post.avatar = u'img/avatar_%s.png' % url
    except:
        pass
    return post

def get_posts(request, id, title):
    '''
    Prints posts
    '''
    posts = []
    following_authors = []
    following_meta_authors = []
    creators = []
    if title == u'Άρθρο':
        '''
        If the post ID is passed in the URL, only
        this post will be shown
        '''
        post = Announcements.objects.get(pk=id)
        '''
        Add creator's URL, mail and avatar in the post
        '''
        post = get_creator(post, post.creator.content_object)
        return [post]
    elif title == u'Ανακοινώσεις':
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
        '''
        Add the school in the following authors as well
        '''
        following_authors.append(request.user.get_profile().school)
    elif title == u'Φοιτητές':
        following_meta_authors.append(request.user.get_profile().students)
    elif title == u'Blog':
        following_authors.append(websites.objects.get(url=u'http://cronos.teilar.gr'))
    elif title == u'Τμήμα':
        following_authors.append(departments.objects.get(url__endswith = '=' + id))
    elif title == u'Καθηγητής':
        following_authors.append(teachers.objects.get(url__endswith = '=' + id))
    '''
    Get authors from the ManyToMany fields
    '''
    for list_of_authors in following_meta_authors:
        for author in list_of_authors.all():
            following_authors.append(author)
    '''
    Find the creators and put them all in a list, so we can retrieve
    all of their posts from a query
    '''
    for author in following_authors:
        author_type = ContentType.objects.get_for_model(author)
        creator = Authors.objects.get(content_type__pk = author_type.id, object_id = author.id)
        creators.append(creator)
    '''
    Get all the posts
    '''
    posts_q = Announcements.objects.filter(creator__in = creators).order_by('-pubdate')
    for post in posts_q:
        '''
        Add creator's URL, mail and avatar in the post
        '''
        post = get_creator(post, post.creator.content_object)
        '''
        Add the post in the list of the wanted posts
        '''
        posts.append(post)
    return posts

@login_required
def posts(request, id, title):
    posts = get_posts(request, id, title)
    return render_to_response('posts.html', {
            'posts': posts,
            'title': title,
        }, context_instance = RequestContext(request))
