# -*- coding: utf-8 -*-

def declaration_update(output):
	from BeautifulSoup import BeautifulSoup

	try:
		soup = BeautifulSoup(output)
		soup1 = BeautifulSoup(str(soup.findAll('table')[14]))
		declaration = []
		declaration.append([])
		for item in soup1.findAll('td', 'error'):
			declaration[0].append(str(item.contents[0]))
		k = 8
		for i in xrange(len(soup1.findAll('span', 'underline'))):
			declaration.append([
				str(soup1.findAll('td')[k].contents[2][6:]),
				str(soup1.findAll('span', 'underline')[i].contents[0]).strip(),
				str(soup1.findAll('td')[k+2].contents[0]),
				str(soup1.findAll('td')[k+3].contents[0]),
				str(soup1.findAll('td')[k+4].contents[0]),
				str(soup1.findAll('td')[k+5].contents[0])
			])
			k += 7
		return declaration
	except:
		return None

def grades_update(output):
	from BeautifulSoup import BeautifulSoup

	try:
		soup = BeautifulSoup(output)
		grades = []
		i = 0
		item = soup.findAll('table')[13].findAll('td')
		length_all_td = len(item)
		semesters = soup.findAll('table')[13].findAll('td', 'groupHeader')
		lessons = soup.findAll('table')[13].findAll('td', 'topBorderLight')
		while i < length_all_td:
			item0 = item[i]
			if item0 in semesters:
				grades.append([str(item0.contents[0])])
			if item0 in lessons:
				year = str(item[i+6].contents[0].i.contents[0]).strip()
				year = year[:10] + year[-9:]
				grades.append([
					str(item0.contents[0]).strip(),
					str(item[i+1].contents[0]).strip(),
					str(item[i+2].contents[0]).strip(),
					str(item[i+3].contents[0]).strip(),
					str(item[i+4].contents[0]).strip(),
					str(item[i+5].span.contents[0]).strip().replace(',', '.'),
					year.replace('--', '-'),
				])
				try:
					if item[i+9].contents[1][-3:] == '(Θ)' or item[i+9].contents[1][-3:] == '(Ε)':
						year = str(item[i+14].contents[0].i.contents[0]).strip()
						year = year[:10] + year[-9:]
						grades.append([
							str(item[i+9].contents[1]).strip(),
							'',
							str(item[i+10].i.contents[0]).strip(),
							str(item[i+11].contents[0]).strip(),
							str(item[i+12].contents[0]).strip(),
							str(item[i+13].contents[0]).strip().replace(',', '.'),
							year.replace('--', '-'),
						])
						year = str(item[i+22].contents[0].i.contents[0])
						year = year[:10] + year[-9:]
						grades.append([
							str(item[i+17].contents[1]).strip(),
							'',
							str(item[i+18].i.contents[0]).strip(),
							str(item[i+19].contents[0]).strip(),
							str(item[i+20].contents[0]).strip(),
							str(item[i+21].contents[0]).strip().replace(',', '.'),
							year.replace('--', '-'),
						])
						i += 11
				except:
					pass
				i += 6
			try:
				if item0.contents[0][:6] == 'Σύνολα':
					grades.append([
						str(item0.b.contents[0]),
						str(item[i+1].contents[1].contents[0]).strip(),
						str(item[i+1].contents[3].contents[0]).strip(),
						str(item[i+1].contents[5].contents[0]).strip(),
						str(item[i+1].contents[7].contents[0]).strip(),
						'total' + str(i),
					])
					i += 1
			except:
				pass
			i += 1

		general = soup.findAll('table')[13].findAll('tr', 'subHeaderBack')[-1]
		grades.append([
			str(general.b.contents[2][-2:]),
			str(general.contents[1].span.contents[0]),
			str(general.contents[1].b.contents[3].contents[0]),
			str(general.contents[1].b.contents[5].contents[0]),
			str(general.contents[1].b.contents[7].contents[0]),
		])
		return grades
	except:
		return None

def eclass_lessons_update(output):
	from BeautifulSoup import BeautifulSoup
	
	try:
		soup = BeautifulSoup(output).find('table', 'FormData')
		eclass_lessons = []
		i = 0
		for item in soup.findAll('a'):
			if (i % 2 == 0):
				eclass_lessons.append(str(item.contents[0].split('-')[0]).strip())
			i += 1
		return eclass_lessons
	except:
		return None
