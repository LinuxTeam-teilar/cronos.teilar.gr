# -*- coding: utf-8 -*-

from BeautifulSoup import BeautifulSoup
from cronos.libraries.log import cronosDebug

logfile = 'update.log'

def declaration_update(output):
	try:
		soup = BeautifulSoup(output)
		soup1 = BeautifulSoup(str(soup.findAll('table')[14]))
		declaration = ''
		temptderror = soup1.findAll('td', 'error')
		temptd = soup1.findAll('td')
		for item in temptderror:
			declaration += item.contents[0] + ','
		k = 9
		tempspanunderline = soup1.findAll('span', 'underline')
		for item in tempspanunderline:
			declaration += '%s,%s,%s,%s,%s,%s,' % (
				temptd[k].contents[2][6:],
				item.contents[0].strip(),
				temptd[k+2].contents[0],
				temptd[k+3].contents[0],
				temptd[k+4].contents[0],
				temptd[k+5].contents[0],
			)
			k += 7
		return declaration[:-1]
	except Exception as error:
		cronosDebug(error, logfile)
		return None

def grades_update(output):
	try:
		soup = BeautifulSoup(output)
		grades = ''
		i = 0
		item = soup.findAll('table')[13].findAll('td')
		length_all_td = len(item)
		semesters = soup.findAll('table')[13].findAll('td', 'groupHeader')
		lessons = soup.findAll('table')[13].findAll('td', 'topBorderLight')
		while i < length_all_td:
			item0 = item[i]
			if item0 in semesters:
				grades += str(item0.contents[0]) + ','
			if item0 in lessons:
				year = str(item[i+6].contents[0].i.contents[0]).strip()
				year = year[:10] + year[-9:]
				grades += '%s,%s,%s,%s,%s,%s,%s,' % (
					str(item0.contents[0]).strip(),
					str(item[i+1].contents[0]).strip(),
					str(item[i+2].contents[0]).strip(),
					str(item[i+3].contents[0]).strip(),
					str(item[i+4].contents[0]).strip(),
					str(item[i+5].span.contents[0]).strip().replace(',', '.'),
					year.replace('--', '-'),
				)
				try:
					if item[i+9].contents[1].strip()[4] in [u'Θ', u'Ε']:
						year = str(item[i+14].contents[0].i.contents[0]).strip()
						year = year[:10] + year[-9:]
						grades += '%s,%s,%s,%s,%s,%s,%s,' % (
							str(item[i+9].contents[1]).strip(),
							'',
							str(item[i+10].i.contents[0]).strip(),
							str(item[i+11].contents[0]).strip(),
							str(item[i+12].contents[0]).strip(),
							str(item[i+13].contents[0]).strip().replace(',', '.'),
							year.replace('--', '-'),
						)
						year = str(item[i+22].contents[0].i.contents[0])
						year = year[:10] + year[-9:]
						grades += '%s,%s,%s,%s,%s,%s,%s,' % (
							str(item[i+17].contents[1]).strip(),
							'',
							str(item[i+18].i.contents[0]).strip(),
							str(item[i+19].contents[0]).strip(),
							str(item[i+20].contents[0]).strip(),
							str(item[i+21].contents[0]).strip().replace(',', '.'),
							year.replace('--', '-'),
						)
						i += 11
				except:
					pass
				i += 6
			try:
				if item0.contents[0][:6] == u'Σύνολα':
					grades += '%s,%s,%s,%s,%s,%s,' % (
						str(item0.b.contents[0]),
						str(item[i+1].contents[1].contents[0]).strip(),
						str(item[i+1].contents[3].contents[0]).strip(),
						str(item[i+1].contents[5].contents[0]).strip(),
						str(item[i+1].contents[7].contents[0]).strip(),
						'total' + str(i),
					)
					i += 1
			except:
				pass
			i += 1

		general = soup.findAll('table')[13].findAll('tr', 'subHeaderBack')[-1]
		grades += '%s,%s,%s,%s,%s,' % (
			str(general.b.contents[2][-2:]),
			str(general.contents[1].span.contents[0]),
			str(general.contents[1].b.contents[3].contents[0]),
			str(general.contents[1].b.contents[5].contents[0]),
			str(general.contents[1].b.contents[7].contents[0]),
		)
		return grades[:-1]
	except Exception as error:
		cronosDebug(error, logfile)
		return None

def eclass_lessons_update(output):
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
