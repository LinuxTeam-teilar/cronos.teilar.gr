# -*- coding: utf-8 -*-
from cronos.refrigerators.forms import Classes
from django.template import RequestContext

def procReq(request):
	forms = {}
	varDict = {}
	for i in Classes:
		forms[i().__class__.__name__] = i(request.POST)
	print "request.method  ===  ", request.method
	if request.method == 'POST':
		for i in forms:
			print forms[i].is_valid(), type(forms[i])
			if forms[i].is_valid():
				for j in forms[i].fields:
					if forms[i].fields[j].__class__.__name__ == "CharField":
						forms[i].fields[j] = eval(request.POST.get(j))
					elif forms[i].fields[j].__class__.__name__ == "ChoiceField":
						forms[i].fields[j] = int(request.POST.get(j))
					elif forms[i].fields[j].__class__.__name__ == "FloatField":
						forms[i].fields[j] = float(request.POST.get(j))
					else:
						print "invalid input"
		print "len(forms) === ", len(forms)
		for i in forms:
			for j in forms[i].fields:
				varDict[j] = forms[i].fields[j]
		print "varDictIF ===", varDict
	else:
		for i in forms:
			for j in forms[i].fields:
				varDict[j] = forms[i].fields[j]
		print "varDictELSE ===", varDict
	return varDict

