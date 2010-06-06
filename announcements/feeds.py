# -*- coding: utf-8 -*-

from django.contrib.syndication.feeds import *
from cronos.announcements.models import Announcements
from django.contrib.auth.models import User
#from cronos.htaccesstest.httpauth import *

class LatestEntries(Feed):
	title = 'Ανακοινώσεις ΤΕΙ Λάρισας'
	link = 'http://cronos.teilar.gr'
	description = 'Ανακοινώσεις διαφόρων ιστοσελίδων του ΤΕΙ Λάρισας. Παρέχονται από το http://cronos.teilar.gr'

#	@logged_in_or_basicauth()
	def items(self, request):
#		print request
#		if request.META['REMOTE_USER']:
#			user_id = request.META['REMOTE_USER']
#			user = users.get_object(username__exact=user_id)
#		else:
#			user = anonymoususers.AnonymousUser()
#		all_announcements = [request.user.get_profile().school]
#		try:
#			all_announcements += request.user.get_profile().eclass_lessons.split(',')
#			all_announcements += request.user.get_profile().other_announcements.split(',')
#			all_announcements += request.user.get_profile().teacher_announcements.split(',')
#		except:
#			pass
#		return Announcements.objects.filter(urlid__urlid__in = all_announcements).order_by('-date_fetched')[:30]
		return Announcements.objects.order_by('-date_fetched')[:30]
	
	def item_author_name(self, item):
		return item.author()
