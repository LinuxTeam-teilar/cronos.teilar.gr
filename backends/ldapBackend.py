# -*- conding: utf-8 -*-

import ldap
from django.contrib.auth.models import User

# Constants
AUTH_LDAP_SERVER = 'ldap://localhost:389'
AUTH_LDAP_BASE_USER = "cn=root,ou=teilarStudents,dc=teilar,dc=com"
AUTH_LDAP_BASE_PASS = "ptixiaki"

class LDAPBackend:
	def authenticate(self, username=None, password=None):
		base = "dc=teilar,dc=com"
		scope = ldap.SCOPE_SUBTREE
		filter = "(&(objectclass=person) (cn=%s))" % username
		ret = None

		# Authenticate the base user so we can search
		try:
			l = ldap.initialize(AUTH_LDAP_SERVER)
			l.protocol_version = ldap.VERSION3
			l.simple_bind_s(AUTH_LDAP_BASE_USER,AUTH_LDAP_BASE_PASS)
		except ldap.LDAPError as detail:
			return detail

		try:
			result_id = l.search(base, scope, filter, ret)
			result_type, result_data = l.result(result_id, 0)
#			while l:
			print result_data
				# If the user does not exist in LDAP, Fail.
			if (result_data == []):
				print 'no'
				return None
			else:
				print 'yes'
				print result_data[0][0]
				# Attempt to bind to the user's DN
			l.simple_bind_s(result_data[0][0],password)

			# The user existed and authenticated. Get the user
			# record or create one with no privileges.
			try:
				user = User.objects.get(username__exact=username)
				
			except:
				# Theoretical backdoor could be input right here. We don't
				# want that, so input an unused random password here.
				# The reason this is a backdoor is because we create a
				# User object for LDAP users so we can get permissions,
				# however we -don't- want them able to login without
				# going through LDAP with this user. So we effectively
				# disable their non-LDAP login ability by setting it to a
				# random password that is not given to them. In this way,
				# static users that don't go through ldap can still login
				# properly, and LDAP users still have a User object.

				from random import choice
				import string
				temp_pass = ""
				for i in range(8):
					temp_pass = temp_pass + choice(string.letters)
				user = User.objects.create_user(username,
					username + '@carthage.edu',temp_pass)
				user.is_staff = False
				user.save()
			# Success.
			return user
		except ldap.INVALID_CREDENTIALS:
			# Name or password were bad. Fail.
			return 'None3'

	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)
		except User.DoesNotExist:
			return None
