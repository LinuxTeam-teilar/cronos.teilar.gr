# -*- coding: utf-8 -*-

import ldap
#from cronos.passwords import *

ldap_user = 'cn=root, dc=teilar, dc=com'
ldap_pass = 'ptixiaki'

class OpenLDAP:
	def login(self):
		ldap_server = 'ldap://localhost:389'
		try:
			l = ldap.open('localhost')
			l.simple_bind_s(ldap_user, ldap_pass)
			return l
		except ldap.LDAPError, error_msg:
			return 'Error: %s' % (error_msg)

	def ldap_search(self, l, keyword):
		base = 'dc=teilar,dc=com'
		scope = ldap.SCOPE_SUBTREE
		filter = 'sn=*' + keyword + '*'
		retrieve_attributes = None
		count = 0
		result_set = []
		timeout = 0
		try:
			result_id = l.search(base, scope, filter, retrieve_attributes)
			while l:
				result_type, result_data = l.result(result_id, timeout)
				if (result_data == []):
					break
				else:
					if result_type == ldap.RES_SEARCH_ENTRY:
						result_set.append(result_data)
			#return result_set
			if len(result_set) == 0:
					return None
			else:
					return result_set
			'''for i in range(len(result_set)):
				for entry in result_set[i]:
					try:
						name = entry[1]['cn'][0]
						email = entry[1]['dionysosUsername'][0]
						count += 1
						return "%d.\nDionysosUsername: %s\n" % (count, email)
					except:
						pass'''
		except ldap.LDAPError, error_msg:
			print 'Error' % (error_msg)
