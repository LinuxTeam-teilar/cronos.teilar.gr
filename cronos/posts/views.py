# -*- coding: utf-8 -*-

from cronos.posts.models import Authors, Posts
from cronos.teilar.models import Departments as departments
from cronos.teilar.models import Teachers as teachers
from cronos.teilar.models import Websites as websites
from cronos.teilar.models import EclassLessons as eclasslessons
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from endless_pagination.decorators import page_template
import mimetypes

def get_creator(post, creator):
    '''
    Add creator's name, URL, mail and avatar in the post dict
    '''
    post.creator_url = creator.url.split('::')[0]
    try:
        if creator.email:
            post.creator_email = creator.email
    except:
        pass
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

def get_enclosure(post):
    try:
        '''
        Fix enclosure's URL from relative to absolute
        '''
        if not post.enclosure.startswith('http://'):
            url = post.url.split('/')[2]
            post.enclosure = 'http://%s/%s' % (url, post.enclosure)
        '''
        Map the enclosure's extension to a known mimetype
        '''
        mimetypes.init()
        extension = '.' + post.enclosure.split('.')[-1]
        post.enclosure_mimetype = mimetypes.types_map[extension]
    except AttributeError:
        post.enclosure = None
    return post

def get_posts(user, id, page):
    '''
    Prints posts
    '''
    posts = []
    following_authors = []
    following_meta_authors = []
    creators = []
    title = []
    if page == u'post':
        '''
        If the post ID is passed in the URL, only
        this post will be shown
        '''
        post = Posts.objects.get(pk=id)
        '''
        Add creator's URL, mail and avatar in the post
        '''
        post = get_creator(post, post.creator.content_object)
        if not user.is_authenticated():
            if post.creator_url != u'http://cronos.teilar.gr':
                return [u'Login Required']
        title = u'Άρθρο'
        return [post, title]
    elif page == u'announcements':
        '''
        The following list has ManyToMany fields from UserProfile. In order
        to get each one of the authors that are included there, we need to
        iterate first the following_meta_authors list, and then iterate each
        one of their contents.
        '''
        following_meta_authors = [
            user.get_profile().following_eclass_lessons,
            user.get_profile().following_teachers,
            user.get_profile().following_websites,
            user.get_profile().following_blogs,
        ]
        '''
        Add the school in the following authors as well
        '''
        following_authors.append(user.get_profile().school)
        title = u'Ανακοινώσεις'
    elif page == u'students':
        following_meta_authors.append(user.get_profile().students)
        title = u'Blogs Φοιτητών'
    elif page == u'blog':
        following_authors.append(websites.objects.get(url=u'http://cronos.teilar.gr'))
        title = u'Blog'
    elif page == u'department':
        department = departments.objects.get(url__endswith = '=' + id)
        following_authors.append(department)
        title = u'Ανακοινώσεις: %s' % department.name
    elif page == u'teacher':
        teacher = teachers.objects.get(url__endswith = '=' + id)
        following_authors.append(teacher)
        title = u'Ανακοινώσεις: %s' % teacher.name
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
    posts_q = Posts.objects.select_related('creator__content_object').filter(creator__in = creators).order_by('-pubdate')
    for post in posts_q:
        '''
        Add creator's URL, mail and avatar in the post
        '''
        post = get_creator(post, post.creator.content_object)
        '''
        Get enclosure URL and mimetype
        '''
        post = get_enclosure(post)
        '''
        Add the post in the list of the wanted posts
        '''
        posts.append(post)
    posts.append(title)
    return posts

@page_template("post_div.html")
def posts(request, id, page, template = "posts.html", extra_context = None):
    '''
    Print a tab with posts, or a single post
    If the user is not authenticated, then he is
    permitted to view only cronos blog and separate
    cronos blog posts
    '''
    if not request.user.is_authenticated():
        if page != u'blog' or page != u'post':
            '''
            Not a cronos blog post or cronos blog tab
            '''
            return HttpResponseRedirect('/login/?next=%s' % request.path)
    posts = get_posts(request.user, id, page)
    title = posts.pop()
    if title == u'Login Required':
        '''
        Not a cronos blog post
        '''
        return HttpResponseRedirect('/login/?next=%s' % request.path)
    context = {'posts': posts, 'title': title}
    if extra_context:
        context.update(extra_context)
    return render_to_response(template, context, context_instance = RequestContext(request))
