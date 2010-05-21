# -*- coding: utf-8 -*-

#from django.http import HttpResponse
#from django.template import Context
#from django.template.loader import get_template
import ldap
from cronos.passwords import *


class OpenLDAP:
	server = 'localhost'
	AUTH_LDAP_SERVER = 'ldap://localhost:389'
	AUTH_LDAP_BASE_USER = "cn=root, dc=teilar, dc=com"
	AUTH_LDAP_BASE_PASS = "ptixiaki"
	keyword = 'test'

try:
	l = ldap.open(server)
	l.simple_bind_s(AUTH_LDAP_BASE_USER, AUTH_LDAP_BASE_PASS)
	print "success"
except:
	print "fail"

def my_search(l, keyword):
	base = 'dc=teilar,dc=com'
	scope = ldap.SCOPE_SUBTREE
	filter = 'description=*' + keyword + '*'
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
		print result_set
		#return result_set
		if len(result_set) == 0:
				print 'No results'
				return
		for i in range(len(result_set)):
			for entry in result_set[i]:
				try:
					name = entry[1]['cn'][0]
					email = entry[1]['dionysosUsername'][0]
					count += 1
					return "%d.\nDionysosUsername: %s\n" % (count, email)
				except:
					pass
	except ldap.LDAPError, error_message:
		print 'fail 2 %s' % (error_message)


#if __name__=='__main1__':
#	main1()

#a = LDAPBackend()

#b = a.authenticate('Theo Chatzimichos', '12345')


def main(request) :
	template = get_template('main.html')
	variables = Context({
		'head_title': my_search(l, keyword),
	})
	output = template.render(variables)
	return HttpResponse(output)
