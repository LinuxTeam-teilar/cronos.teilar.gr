# -*- coding: utf-8 -*-
from cronos.refrigerators.forms import Classes
from django.template import RequestContext

def procReq(request):
	if request.method == 'POST':
		forms['form1'] = Classes[0](request.POST)
		forms['form2'] = Classes[1](request.POST)
		forms['form3'] = Classes[2](request.POST)
		forms['form4'] = Classes[3](request.POST)
		forms['form5'] = Classes[4](request.POST)
		forms['form6'] = Classes[5](request.POST)
		forms['form7'] = Classes[6](request.POST)
		forms['form8'] = Classes[7](request.POST)
		forms['form9'] = Classes[8](request.POST)
		forms['form10'] = Classes[9](request.POST)
		forms['form11'] = Classes[10](request.POST)
		forms['form12'] = Classes[11](request.POST)
		forms = {}
		for i in Classes:
			forms[i().__class__.__name__] = i(request.POST)
		for i in forms:
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
		varDict = {}
		for i in forms:
			if forms[i].is_valid():
				for j in forms[i].base_fields:
					varDict[j] = forms[i].base_fields[j]
	else:
		forms['form1'] = Classes[0](request.POST)
		forms['form2'] = Classes[1](request.POST)
		forms['form3'] = Classes[2](request.POST)
		forms['form4'] = Classes[3](request.POST)
		forms['form5'] = Classes[4](request.POST)
		forms['form6'] = Classes[5](request.POST)
		forms['form7'] = Classes[6](request.POST)
		forms['form8'] = Classes[7](request.POST)
		forms['form9'] = Classes[8](request.POST)
		forms['form10'] = Classes[9](request.POST)
		forms['form11'] = Classes[10](request.POST)
		forms['form12'] = Classes[11](request.POST)
	return varDict

