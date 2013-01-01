# -*- coding: utf-8 -*-

# ex Psugeia[1-6]Form - FormA
# ex Psugeia7Form - FormB
# ex Psugeia8Form - FormC
# ex Psugeia9Form - FormD
# ex Psugeia10Form - FormE
# ex Psugeia11Form - FormF
# ex Psugeia12Form - FormG

from django import forms
import xml.etree.ElementTree as ET
from cronos.settings import *
xmlfile = '' + str(PROJECT_ROOT.split()[0][0:len(PROJECT_ROOT)-2]) + 'refrigerators/Refrigerators.xml'
tree = ET.parse(xmlfile)
root = tree.getroot()

# ex Dicts.
Forms = []
# ex Forms.
Classes = []
# the second, undeclared, half of each ex dict_X_.
tempdict = {}

for a_form in root:
	varDict = {}
	funcDict = {}
	for a_var in a_form:
		#print a_var.attrib['type']
		if a_var.tag == "var":
			if a_var.attrib['type'] == 'float':
				varsForm = forms.FloatField(label = a_var._children[0].__dict__['attrib']['label'], help_text = a_var._children[0].__dict__['attrib']['help_text'])
			elif a_var.attrib['type'] == 'choice':
				choices = eval(a_var._children[0].__dict__['attrib']['choices'])
				varsForm = forms.ChoiceField(choices = choices, label = a_var._children[0].__dict__['attrib']['label'], help_text = a_var._children[0].__dict__['attrib']['help_text'])
			elif a_var.attrib['type'] == 'tuple':
				varsForm = eval(a_var._children[0].__dict__['attrib']['values'])
			else:
				pass
			#print a_var.attrib['name'], type(varsForm)
			varDict[a_var.attrib['name']] = varsForm
		elif a_var.tag == "function":
			#funcForm = eval(a_var._children[0].__dict__['attrib']['equation'])
			funcname = a_var.__dict__['attrib']['name']
			funcForm = a_var.__dict__['attrib']['equation']
			funcDict[funcname] = funcForm
		else:
			pass
	fullclass = (a_form.attrib['name'], varDict, funcDict)
	#print tempForm, ' -type> ', type(tempForm)
	#print tempForm
	Forms.append(fullclass)

for i in Forms:
    Classes.append(type(i[0], (forms.Form, ), i[1]))
#type(Classes[0].sint_thermop)

