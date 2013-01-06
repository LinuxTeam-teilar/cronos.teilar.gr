# -*- coding: utf-8 -*-
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


def fixEquationSyntax(self, com):
	ll=[]
	buff=''
	flag = 0
	i=0
	fstr=''
	com = com + ' '
	forbBuffDict = ["False", "True", "and", "or", "not"]
	while i!=len(com):
		if com[i] == '_' or ((com[i].isdigit() == True) or (com[i].isalpha() == True)) or ((com[i]=='[') or com[i]=='.') or com[i] == ']':
			if com[i] == ']':
				buff = buff + com[i]
				flag = 1
			else:
				buff = buff + com[i]
				flag = 0
		elif com[i] == ' ':
			flag = 1
			fstr = fstr + com[i]
		else:
			flag = 1
			if com[i] == ')':
				temp = com[i]
		if buff != '' and flag == 1:
			# filter float number out of the dict.
			if (((buff.isalnum() == False) and buff[0].isalpha() == False)) or buff.isdigit() == True:
				pass
			else:
				buff_no_white = ''.join(buff.split())
				if buff_no_white not in forbBuffDict:
					if buff.find('[') >= 0 and buff.find(']') >= 0:
						limits = (buff.find('['), buff.find(']')+1)
						buff = "self.base_fields['" + buff[0:limits[0]] + "']" + buff[limits[0]:limits[1]]
						ll.append(buff)
					else:
						buff = "self.base_fields['" + buff + "']"
						ll.append(buff)
			if com[i] == ')':
				fstr = fstr + buff + temp
			else:
				fstr = fstr + buff
			buff = ''
		elif flag == 1:
			fstr = fstr + com[i]
		else:
			pass
		i = i + 1
	return fstr

def evalEquations(self):
	results = {}
	estr = ''
	cstr = ''
	for i in self.results:
		cstr = self.fixEquationSyntax(str(self.results[i][1]))
		if eval(cstr):
			fstr = self.fixEquationSyntax(self.results[i][0])
			self.results[i] = eval(fstr)


for a_form in root:
	varDict = {}
	resultsDict = {}
	for a_tag in a_form:
		#print a_tag.attrib['type']
		if a_tag.tag == "var":
			if a_tag.attrib['type'] == 'float':
				varsForm = forms.FloatField(label = a_tag._children[0].__dict__['attrib']['label'], help_text = a_tag._children[0].__dict__['attrib']['help_text'])
			elif a_tag.attrib['type'] == 'choice':
				choices = eval(a_tag._children[0].__dict__['attrib']['choices'])
				varsForm = forms.ChoiceField(choices = choices, label = a_tag._children[0].__dict__['attrib']['label'], help_text = a_tag._children[0].__dict__['attrib']['help_text'])
			elif a_tag.attrib['type'] == 'text':
				varsForm = forms.CharField(label = a_tag._children[0].__dict__['attrib']['label'], help_text = a_tag._children[0].__dict__['attrib']['help_text'])
			else:
				pass
			varDict[a_tag.attrib['name']] = varsForm
		elif a_tag.tag == "results":
			for a_case in a_tag:
				resultsDict[a_case.__dict__['attrib']['name']] = (a_case.__dict__['attrib']['equation'], a_case.__dict__['attrib']['condition'])
			# The below "varDict['results']" is a dict-in-a-dict and the "dictWithEquations" arg for the "evalEquation" function.
			varDict['results'] = resultsDict
		else:
			pass
	varDict['evalEquations'] = evalEquations
	varDict['fixEquationSyntax'] = fixEquationSyntax
	fullclass = (a_form.attrib['name'], varDict)
	Forms.append(fullclass)

for i in Forms:
	Classes.append(type(i[0], (forms.Form, ), i[1]))