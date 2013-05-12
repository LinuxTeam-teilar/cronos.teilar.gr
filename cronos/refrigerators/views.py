# -*- coding: utf-8 -*-

from cronos.refrigerators.forms import *
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from cronos.refrigerators.forms import Classes


def refrigerators(request):
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
					forms[i].fields[j].__dict__['initial'] = 5.0
					if forms[i].fields[j].__class__.__name__ == "CharField":
						forms[i].fields[j].__dict__['initial'] = eval(request.POST.get(j))
					elif forms[i].fields[j].__class__.__name__ == "FloatField":
						forms[i].fields[j].__dict__['initial'] = float(request.POST.get(j))
						#print "\n\n\t FLOAT var ==", float(request.POST.get(j)), "\n\t initial value from request ==", forms[i].fields[j].__dict__['initial'], "\n\t VAR_NAME == ", j, "-.-"
					elif forms[i].fields[j].__class__.__name__ == "ChoiceField":
						print "\nChoiceField\n"
					else:
						print "\ninvalid formField \n"
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
		print "\n\n form2.fields['sint_thermop2'].__dict__['initial'] = ", varDict['form2'].fields['sint_thermop2'].__dict__['initial'], "\n\n"
		print "\n\n evalEquations() = ", varDict['form2'].evalEquations()
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
	# 'XMLFILENAME' will be replaced by the urls./extensions(ex-refrigerators)
	# /UserSelectedURL(e.g. refiregerators)/.
	return render_to_response('refrigerators.html', varDict, context_instance = RequestContext(request))
