# -*- coding: utf-8 -*-

from django.contrib.syndication.feeds import *
from cronos.announcements.models import Announcements

class LatestEntries(Feed):
	title = 'Ανακοινώσεις ΤΕΙ Λάρισας'
	link = 'http://cronos.teilar.gr'
	description = 'Ανακοινώσεις διαφόρων ιστοσελίδων του ΤΕΙ Λάρισας. Παρέχονται από το http://cronos.teilar.gr'

	def items(self):
		return Announcements.objects.order_by('-date_fetched')[:200]

	def item_author_name(self, item):
		return item.author()
