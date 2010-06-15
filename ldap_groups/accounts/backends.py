# -*- coding: utf-8 -*-

from cronos.ldap_groups.models import LDAPGroup
from cronos.user.models import LdapProfile
from django.conf import settings
from django.contrib.auth.models import User, Group
import ldap
import ldap.filter

class BaseGroupMembershipBackend(object):
	"""
	Base class for implementing an authentication backend which authenticates
	against LDAP and sets Django group membership based on LDAP Organizational
	Unit (OU) membership.
	"""
	def authenticate(self, username=None, password=None):
		"""
		Attempts to bind the provided username and password to LDAP.
		
		A successful LDAP bind authenticates the user.
		"""
		raise NotImplementedError
	
	def bind_ldap(self, username, password):
		"""
		Implements the specific logic necessary to bind a given username and
		password to the particular LDAP server.
		
		Override this method for each new variety of LDAP backend.
		"""
		raise NotImplementedError
	
	def get_or_create_user(self, username, password):
		"""
		Attempts to get the user from the Django db; failing this, creates a
		django.contrib.auth.models.User from details pulled from the specific
		LDAP backend.
		
		Override this method for each new variety of LDAP backend.
		"""
		raise NotImplementedError
	
	def get_user(self, user_id):
		"""
		Implements the logic to retrieve a specific user from the Django db.
		"""
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None
		
	def set_memberships_from_ldap(self, user, membership):
		"""
		Assigns user to specific django.contrib.auth.models.Group groups based
		on ldap_group mappings created by the site admin, also assigns staff
		or superuser privileges based on those same mappings.
		"""
		ldap_groups = LDAPGroup.objects.filter(org_unit__in=membership)
		for l_grp in ldap_groups:
			for grp in l_grp.groups.all():
				user.groups.add(grp)
				
		staff_groups = ldap_groups.filter(make_staff=True).count()
		if staff_groups > 0:
			user.is_staff = True
			
		superuser_groups = ldap_groups.filter(make_superuser=True).count()
		if superuser_groups > 0:
			user.is_superuser = True
		user.save()
		

class ActiveDirectoryGroupMembershipSSLBackend(BaseGroupMembershipBackend):
	def bind_ldap(self, username, password):
		try:
			ldap.set_option(ldap.OPT_X_TLS_CACERTFILE,settings.CERT_FILE)
		except AttributeError:
			pass
		ldap.set_option(ldap.OPT_REFERRALS,0)
		l = ldap.initialize(settings.LDAP_URL)
		l.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
		binddn = "uid=%s,%s" % (username, settings.SEARCH_DN)
		l.simple_bind_s(binddn,password)
		return l
		
	def authenticate(self,username=None,password=None):
		try:
			if len(password) == 0:
				return None
			l = self.bind_ldap(username, password)
			l.unbind_s()
			return self.get_or_create_user(username,password)

		except ImportError:
			pass
		except ldap.INVALID_CREDENTIALS as e:
			pass
	
	def get_or_create_user(self, username, password):
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:

			try:
				l = self.bind_ldap(username, password)

				# search
				result = l.search_s(settings.SEARCH_DN, ldap.SCOPE_SUBTREE, "(uid=%s)" % (username), ['*'])[0][1]

				first_name = result['cn'][0]

				last_name = result['sn'][0]

				dionysos_username = result['dionysosUsername'][0]

				dionysos_password = result['dionysosPassword'][0]

				introduction_year = result['introductionYear'][0]

				registration_number = result['registrationNumber'][0]

				school = result['school'][0]

				semester = result['semester'][0]

				if result.has_key('declaration'):
					declaration = ','.join(result['declaration'])
				else:
					declaration = None
				
				if result.has_key('eclassUsername'):
					eclass_username = result['eclassUsername'][0]
					eclass_password = result['eclassPassword'][0]	
					if result.has_key('eclassLessons'):
						eclass_lessons = ','.join(result['eclassLessons'])
					else:
						eclass_lessons = None
				else:
					eclass_username = None
					eclass_password = None
					eclass_lessons = None

				if result.has_key('webmailUsername'):
					mail = result['webmailUsername'][0] + '@teilar.gr'
					webmail_username = result['webmailUsername'][0]
					webmail_password = result['webmailPassword'][0]
				else:
					mail = '%s@notapplicablemail.com' % (username)
					webmail_username = None
					webmail_password = None

				if result.has_key('teacherAnnouncements'):
					teacher_announcements = ','.join(result['teacherAnnouncements'])
				else:
					teacher_announcements = None

				if result.has_key('otherAnnouncements'):
					other_announcements = ','.join(result['otherAnnouncements'])
				else:
					other_announcements = None

				l.unbind_s()

				user = User(
					username = username,
					first_name = first_name,
					last_name = last_name,
					email = mail,
				)

			except Exception, e:
				return None

			user.is_staff = False
			user.is_superuser = False
			user.set_password(password)
			user.save()
			userprofile = LdapProfile(
				user = user,
				dionysos_username = dionysos_username,
				dionysos_password = dionysos_password,
				introduction_year = introduction_year,
				registration_number = registration_number,
				school = school,
				semester = semester,
				declaration = declaration,
				eclass_username = eclass_username,
				eclass_password = eclass_password,
				eclass_lessons = eclass_lessons,
				webmail_username = webmail_username,
				webmail_password = webmail_password,
				teacher_announcements = teacher_announcements,
				other_announcements = other_announcements,
			)
			userprofile.save()

#			self.set_memberships_from_ldap(user, membership)
		
		return user

class eDirectoryGroupMembershipSSLBackend(BaseGroupMembershipBackend):
	def bind_ldap(self, username, password):
		try:
			ldap.set_option(ldap.OPT_X_TLS_CACERTFILE,settings.CERT_FILE)
		except AttributeError:
			pass
		l = ldap.initialize(settings.LDAP_URL)
		l.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
		l.simple_bind_s(username, password)
		return l

	def authenticate(self,username=None,password=None):
		try:
			if len(password) == 0:
				return None
			l = self.bind_ldap(settings.BIND_USER, settings.BIND_PASSWORD)
			base = settings.SEARCH_DN
			scope = ldap.SCOPE_SUBTREE
			retrieve_attributes = ['cn']

			filtered_name = ldap.filter.escape_filter_chars(username)
			filter = 'cn=%s' % filtered_name

			results = l.search_s(base, scope, filter, retrieve_attributes)
			candidate_dns = [result[0] for result in results]

			l.unbind()
			for dn in candidate_dns:
				try:
					l = ldap.initialize(settings.LDAP_URL)
					l.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
					l.simple_bind_s(dn, password)
				except ldap.INVALID_CREDENTIALS:
					l.unbind()
					continue
				l.unbind()
				return self.get_or_create_user(dn, password)

		except ImportError:
			pass
		except ldap.INVALID_CREDENTIALS:
			pass

	def get_or_create_user(self, username, password):
		stripped_name = ''
		if username.lower().startswith('cn='):
			stripped_name = username.split(',')[0][3:].lower()
		try:
			user = User.objects.get(username=stripped_name)
		except User.DoesNotExist:
			try:
				l = self.bind_ldap(settings.BIND_USER, settings.BIND_PASSWORD)
				# search
				result = l.search_ext_s(settings.SEARCH_DN,
										ldap.SCOPE_SUBTREE,
										"cn=%s" % stripped_name,
										settings.SEARCH_FIELDS)[0][1]
				l.unbind_s()

				if result.has_key('groupMembership'):
					membership = result['groupMembership']
				else:
					membership = None

				# get email
				if result.has_key('mail'):
					mail = result['mail'][0]
				else:
					mail = None

				# get surname
				if result.has_key('sn'):
					last_name = result['sn'][0]
				else:
					last_name = None

				# get display name
				if result.has_key('givenName'):
					first_name = result['givenName'][0]
				else:
					first_name = None


				user = User(username=stripped_name,first_name=first_name,last_name=last_name,email=mail)
			except Exception, e:
				return None

			user.is_staff = False
			user.is_superuser = False
			user.set_password('ldap authenticated')
			user.save()

			self.set_memberships_from_ldap(user, membership)

		return user

