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
			print forms[i].is_valid(), " || ", type(forms[i]), " || ", forms[i].errors, " || "
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
			formsname = ''
			for k in str(type(forms[i]))[27:]:
				if k.isdigit()>0 or k.isalpha()>0:
					formsname=formsname+k
				else:
					pass
			varDict[formsname] = forms[i]
		print "\n\tvarDictIF ===\n"
	else:
		for i in forms:
			formsname = ''
			for k in str(type(forms[i]))[27:]:
				if k.isdigit()>0 or k.isalpha()>0:
					formsname=formsname+k
				else:
					pass
				varDict[formsname] = forms[i]
		print "\n\tvarDictELSE ===\n\n\n", varDict
	return varDict

