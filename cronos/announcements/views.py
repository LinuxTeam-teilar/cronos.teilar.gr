# -*- coding: utf-8 -*-

from cronos.announcements.models import Authors, Announcements
from cronos.announcements.forms import AnnouncementForm
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
    form = AnnouncementForm()
    announcements = []
    if request.GET.get('announcement_id'):
        '''
        If the announcement ID is passed in the hidden form, only
        this announcement will be shown
        '''
        announcement_id = request.GET.get('announcement_id')
        form = AnnouncementForm(request.GET)
        announcements.append(Announcements.objects.get(pk = announcement_id).__dict__)
    else:
        '''
        Get a list of following authors
        '''
        following_authors = [request.user.get_profile().school]
        for author in following_authors:
            '''
            Find the creator
            '''
            author_type = ContentType.objects.get_for_model(author)
            creator = Authors.objects.get(content_type__pk = author_type.id, object_id = author.id)
            for item in Announcements.objects.filter(creator = creator).order_by('-pubdate')[:30]:
                '''
                Add the announcement in the list of the wanted announcements
                '''
                announcements.append(item.__dict__)
    return render_to_response('announcements.html', {
            'announcements': announcements,
            'form': form,
        }, context_instance = RequestContext(request))
