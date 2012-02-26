# -*- coding: utf-8 -*-

from proj_root import *
import os
import sys
sys.path.append(PROJECT_ROOT)
os.environ['DJANGO_SETTINGS_MODULE'] = 'cronos.settings'
from cronos.announcements.models import *
from cronos.libraries.log import cronosDebug
from django.conf import settings
from django.db.utils import IntegrityError
from BeautifulSoup import BeautifulSoup
import MySQLdb
import pycurl
import re
import StringIO
import tempfile
import time
import urllib
import urlparse

conn = pycurl.Curl()
p = re.compile(r'<[^<]*?/?>')

date_full = time.strftime('%Y%m%d-%H%M')
date_minimal = time.strftime('%Y%m')
logfile = 'cron_announcements/%s/cron_announcements-%s.log' % (date_minimal, date_full)
success = True

def getid(id, i):
    for item in Id.objects.filter(urlid__exact = (id + str(i))):
        return item

def geteclassid(i):
    for item in Id.objects.filter(urlid__exact = i):
        return item

def www_teilar_gr():
    dest = ['http://www.teilar.gr/']
    for cid in xrange(30):
        if (cid != 0):
            dest.append('http://www.teilar.gr/tmimatanews.php?cid=' + str(cid))
        b = StringIO.StringIO()
        conn.setopt(pycurl.URL, dest[cid])
        conn.setopt(pycurl.WRITEFUNCTION, b.write)
        conn.perform()
        output = unicode(b.getvalue(), 'utf-8', 'ignore')
        soup = BeautifulSoup(str(BeautifulSoup(output).findAll('td', 'LineDownDots')))
        i = 0
        templinedowndots = soup.findAll('td', 'LineDownDots')
        temptdblacktext11 = soup.findAll('td', 'BlackText11')
        tempablacktext11 = soup.findAll('a', 'BlackText11')
        for item in templinedowndots:
            url = 'http://www.teilar.gr/' + str(temptdblacktext11[i].contents[0]).split('"')[3].replace('&amp;', '&')

            #parse each announcement
            b = StringIO.StringIO()
            conn.setopt(pycurl.URL, url)
            conn.setopt(pycurl.WRITEFUNCTION, b.write)
            conn.perform()
            output = unicode(b.getvalue(), 'utf-8', 'ignore')
            soup1 = BeautifulSoup(output)
            description = ''
            attachment_text = ''
            attachment_url = ''
            if soup1.find('td', 'BlackText11'):
                description = str(soup1.find('td', 'BlackText11'))
                description = p.sub(' ', description)
            if soup1.find('a', 'BlackText11Bold'):
                attachment_text = str(soup1.find('a', 'BlackText11Bold').contents[0])
                attachment_url = 'http://www.teilar.gr/' + str(soup1.find('a', 'BlackText11Bold')).split('"')[3]
            title = str(tempablacktext11[i].contents[0]).strip()
            teilar_gr = Announcements(
                title = title,
                url = url,
                unique = url,
                urlid = getid('cid', cid),
                description = description.strip(),
                attachment_text = attachment_text,
                attachment_url = attachment_url,
            )
            try:
                teilar_gr.save()
                status = 'NEW: %s from: %s' % (title, str(getid('cid', cid)))
                print status
                cronosDebug(status, logfile)
            except IntegrityError:
                pass
            except MySQLdb.Warning, warning:
                status = 'NEW: %s from: %s' % (title, str(getid('cid', cid)))
                print status
                cronosDebug(status, logfile)
                warningstatus = 'WARNING: %s\n' % str(warning)
                print warningstatus
                cronosDebug(warningstatus, logfile)
                success = False
                pass
            except Exception as error:
                errorstatus = 'ERROR: %s  %s' % (title, str(error))
                print errorstatus
                cronosDebug(errorstatus, logfile)
                success = False
                pass
            i += 1

def professors():
    for pid in xrange(350):
        url = 'http://www.teilar.gr/person_announce.php?pid=' + str(pid)
        b = StringIO.StringIO()
        conn.setopt(pycurl.URL, url)
        conn.setopt(pycurl.WRITEFUNCTION, b.write)
        conn.perform()
        output = unicode(b.getvalue(), 'utf-8', 'ignore')
        soup = BeautifulSoup(output)
        templinedowndots = soup.findAll('td', 'LineDownDots')
        for item in templinedowndots:
            soup1 = BeautifulSoup(str(item))
            description = ''
            attachment_text = ''
            attachment_url = ''
            unique = ''
            if len(str(soup1.findAll('td', 'BlackText11')[1])) > 5:
                description = str(soup1.findAll('td', 'BlackText11')[1])
                description = p.sub(' ', description)
            try:
                attachment_text = str(soup1.findAll('td', 'BlackText11')[2].contents[0].contents[0].contents[0])
                attachment_url = 'http://www.teilar.gr/' + str(soup1.findAll('td', 'BlackText11')[2].contents[0].contents[0]).split('"')[3]
            except:
                pass
            if len(description) == 0:
                unique = attachment_url
            else:
                unique = description.strip()
            try:
                title = str(soup1.findAll('td', 'BlackText11')[0].contents[0].contents[0]).strip()
            except IndexError:
                title = ''
            teachers_teilar_gr = Announcements(
                title = title,
                urlid = getid('pid', pid),
                description = description.strip(),
                unique = unique,
                attachment_text = attachment_text,
                attachment_url = attachment_url,
                url = url,
            )
            try:
                teachers_teilar_gr.save()
                status = 'NEW: %s from: %s' % (title, str(getid('pid', pid)))
                print status
                cronosDebug(status, logfile)
            except IntegrityError:
                pass
            except MySQLdb.Warning, warning:
                status = 'NEW: %s from: %s' % (title, str(getid('pid', pid)))
                print status
                cronosDebug(status, logfile)
                warningstatus = 'WARNING: %s' % str(warning)
                print warningstatus
                cronosDebug(warningstatus, logfile)
                success = False
                pass
            except Exception as error:
                errorstatus = 'ERROR: %s %s' % (title, str(error))
                print errorstatus
                cronosDebug(error, logfile)
                success = False
                pass

def eclass_teilar_gr():
    b = StringIO.StringIO()
    fd, cookie_path = tempfile.mkstemp(prefix='eclass_', dir='/tmp')
    login_form_seq = [
        ('uname', settings.ECLASS_USER),
        ('pass', settings.ECLASS_PASSWORD),
        ('submit', 'E%95%CE%AF%CF%83%CE%BF%CE%B4%CE%BF%CF%82'),
    ]
    login_form_data = urllib.urlencode(login_form_seq)
    conn.setopt(pycurl.FOLLOWLOCATION, 1)
    conn.setopt(pycurl.COOKIEFILE, cookie_path)
    conn.setopt(pycurl.COOKIEJAR, cookie_path)
    conn.setopt(pycurl.URL, 'http://openclass.teilar.gr/index.php')
    conn.setopt(pycurl.POST,1)
    conn.setopt(pycurl.POSTFIELDS, login_form_data)
    conn.setopt(pycurl.WRITEFUNCTION, b.write)
    conn.perform()
    output = unicode(b.getvalue(), 'utf-8', 'ignore')
    soup = BeautifulSoup(output).find('table', 'FormData')
    i = 0
    tempa = soup.findAll('a')
    for item in tempa:
        if (i%2 == 0):
            cid = str(item.contents[0]).split('-')[0].strip()
            url = 'http://openclass.teilar.gr/index.php?perso=2&c=' + cid
            b = StringIO.StringIO()
            conn.setopt(pycurl.FOLLOWLOCATION, 1)
            conn.setopt(pycurl.COOKIEFILE, cookie_path)
            conn.setopt(pycurl.COOKIEJAR, cookie_path)
            conn.setopt(pycurl.URL, url)
            conn.setopt(pycurl.POST, 1)
            conn.setopt(pycurl.COOKIE, cookie_path)
            conn.setopt(pycurl.POSTFIELDS, login_form_data)
            conn.setopt(pycurl.WRITEFUNCTION, b.write)
            conn.perform()
            output = unicode(b.getvalue(), 'utf-8', 'ignore')
            # in case there are no announcements for the specific lesson
            if not (BeautifulSoup(output).find('p', 'alert1')):
                soup1 = BeautifulSoup(output).find('table')
                j = 0
                k = 1
                tempsmall = soup1.findAll('small')
                for item in tempsmall:
                    description = ''
                    unique = ''
                    title = ''
                    l = 0
                    # in case there is another table/td inside the announcement OR there is no content
                    temptd = soup1.findAll('td')
                    try:
                        for item1 in temptd[k].contents:
                            description += str(temptd[k].contents[l])
                            l += 1
                        description = p.sub(' ', description).strip()
                        description = ''.join(description.split(')')[1:])
                    except IndexError:
                        pass
                    # in case there is no title
                    try:
                        if (len(str(temptd[k].b)) > 8):
                            title = temptd[k].b.contents[0].strip()
                        else: 
                            title = ''
                    except IndexError:
                        pass
                    if not description:
                        unique = title
                    else:
                        unique = description
                    eclass_teilar_gr = Announcements(
                        title = title,
                        urlid = geteclassid(cid),
                        description = description,
                        unique = unique,
                        url = url,
                        attachment_url = '',
                        attachment_text = ''
                    )
                    try:
                        eclass_teilar_gr.save()
                        status = 'NEW: %s from: %s' % (title, geteclassid(cid))
                        print status
                        cronosDebug(status, logfile)
                    except IntegrityError:
                        pass
                    except MySQLdb.Warning, warning:
                        status = 'NEW: %s from %s' % (title, geteclassid(cid))
                        print status
                        cronosDebug(status, logfile)
                        warningstatus = 'WARNING: %s' % str(warning)
                        print warningstatus
                        cronosDebug(warningstatus, logfile)
                        success = False
                        pass
                    except Exception as error:
                        errorstatus = 'ERROR: %s %s' % (title, str(error))
                        print errorstatus
                        cronosDebug(error, logfile)
                        success = False
                        pass
                    j += 1
                    k += 2
        i += 1

def noc_teilar_gr():
    b = StringIO.StringIO()
    conn.setopt(pycurl.URL, 'http://noc-portal.teilar.gr/index.php?option=com_content&task=category&sectionid=1&id=29&Itemid=89')
    conn.setopt(pycurl.WRITEFUNCTION, b.write)
    conn.perform()
    output = (b.getvalue()).decode('windows-1253')
    soup = BeautifulSoup(output)
    for i in xrange(2):
        for j in xrange(5):
            tempurl = soup.findAll('tr', 'sectiontableentry' + str(i + 1))[j].contents[1].contents[1]
            url = str(tempurl).split('"')[1].replace('&amp;', '&')
            b = StringIO.StringIO()
            conn.setopt(pycurl.URL, url)
            conn.setopt(pycurl.WRITEFUNCTION, b.write)
            conn.perform()
            output = (b.getvalue()).decode('windows-1253')
            soup1 = BeautifulSoup(output)
            description = str(soup1.findAll('table', 'contentpaneopen')[1])
            description = p.sub(' ', description)
            title = str(tempurl.contents[0]).strip()
            name = getid('cid', 50)
            noc_teilar_gr = Announcements(
                title = title,
                url = url,
                unique = url,
                urlid = name,
                description = description.strip(),
                attachment_text = '',
                attachment_url = '',
            )
            try:
                noc_teilar_gr.save()
                status = 'NEW: %s from: %s' % (title, name)
                print status
                cronosDebug(status, logfile)
            except IntegrityError:
                pass
            except MySQLdb.Warning, warning:
                status = 'NEW: %s from %s' % (title, name)
                print status
                cronosDebug(status,logfile)
                warningstatus = 'WARNING: %s' % str(warning)
                print warningstatus
                cronosDebug(warningstatus, logfile)
                success = False
                pass
            except Exception as error:
                errorstatus = 'ERROR: %s %s' % (title, str(error))
                print errorstatus
                cronosDebug(errorstatus, logfile)
                success = False
                pass

def career_teilar_gr():
    b = StringIO.StringIO()
    conn.setopt(pycurl.URL, 'http://www.career.teilar.gr/newslist.php')
    conn.setopt(pycurl.WRITEFUNCTION, b.write)
    conn.perform()
    output = unicode(b.getvalue(), 'utf-8', 'ignore')
    soup = BeautifulSoup(str(BeautifulSoup(output).findAll('table')[5]))
    tempa = soup.findAll('a')
    for i in xrange(20):
        url = 'http://www.career.teilar.gr/' + str(tempa[i]).split('"')[1]
        b = StringIO.StringIO()
        conn.setopt(pycurl.URL, url)
        conn.setopt(pycurl.WRITEFUNCTION, b.write)
        conn.perform()
        output = unicode(b.getvalue(), 'utf-8', 'ignore')
        soup1 = BeautifulSoup(output)

        main_text = ''

        main_text = str(soup1.findAll('table')[5])
        main_text = p.sub(' ', main_text)
        name = getid('cid', 51)
        title = soup.findAll('a')[i].contents[0]

        career_teilar_gr = Announcements(
            title = title,
            url = url,
            unique = url,
            urlid = name,
            description = main_text.strip(),
            attachment_text = '',
            attachment_url = '',
        )
        try:
            career_teilar_gr.save()
            status = 'NEW: %s from: %s' % (title, name)
            print status
            cronosDebug(status, logfile)
        except IntegrityError:
            pass
        except MySQLdb.Warning, warning:
            status = 'NEW: %s from %s' % (title, name)
            print status
            cronosDebug(status,logfile)
            warningstatus = 'WARNING: %s' % warning
            print warningstatus
            cronosDebug(warningstatus, logfile)
            success = False
            pass
        except Exception as error:
            errorstatus = 'ERROR: %s %s' % (title, error)
            print errorstatus
            cronosDebug(errorstatus, logfile)
            success = False
            pass

def linuxteam_cs_teilar_gr():
    b = StringIO.StringIO()
    conn.setopt(pycurl.URL, 'http://linuxteam.cs.teilar.gr')
    conn.setopt(pycurl.WRITEFUNCTION, b.write)
    conn.perform()
    output = b.getvalue()
    soup = BeautifulSoup(str(BeautifulSoup(output).findAll('h2', 'title')))

    for i in range(4, 7):
        link = 'http://linuxteam.cs.teilar.gr' + str(soup.findAll('h2', 'title')[i].contents[0]).split('"')[1]

        b = StringIO.StringIO()
        conn.setopt(pycurl.URL, link)
        conn.setopt(pycurl.WRITEFUNCTION, b.write)
        conn.perform()
        output = b.getvalue()
        soup1 = BeautifulSoup(output)
        main_text = ''
        main_text = str(soup1.findAll('div', 'content')[4].contents[0])
        main_text = p.sub(' ', main_text)
        name = getid('cid', 52)
        title = soup.findAll('h2', 'title')[i].contents[0].contents[0]

        linuxteam_teilar_gr = Announcements(
            title = title,
            url = link,
            unique = link,
            urlid = name,
            description = main_text.strip(),
            attachment_text = '',
            attachment_url = '',
        )
        try:
            linuxteam_teilar_gr.save()
            status = 'NEW: %s from: %s' % (title, name)
            print status
            cronosDebug(status, logfile)
        except IntegrityError:
            pass
        except MySQLdb.Warning, warning:
            status = 'NEW: %s from %s' % (title, name)
            print status
            cronosDebug(status,logfile)
            warningstatus = 'WARNING: %s' % warning
            print warningstatus
            cronosDebug(warningstatus, logfile)
            success = False
            pass
        except Exception as error:
            errorstatus = 'ERROR: %s %s' % (title, str(error))
            print errorstatus
            cronosDebug(errorstatus, logfile)
            success = False
            pass

def dionysos_teilar_gr():
    link = 'http://dionysos.teilar.gr/Menu/r1.htm'

    b = StringIO.StringIO()
    conn.setopt(pycurl.URL, link)
    conn.setopt(pycurl.WRITEFUNCTION, b.write)
    conn.perform()
    output = (b.getvalue()).decode('windows-1253')
    soup = BeautifulSoup(str(BeautifulSoup(output).findAll('table')[1]))

    for i in xrange(len(soup.findAll('th')) - 1):
        main_text = ''
        for item in soup.findAll('th')[i+1].b.contents:
            main_text += str(item)
        main_text = p.sub(' ', main_text)
        name = getid('cid', 53)

        dionysos_teilar_gr = Announcements(
            title = 'No Title',
            url = link,
            urlid = name,
            description = main_text.strip(),
            unique = 'dionysos' + main_text.strip(),
            attachment_url = '',
            attachment_text = '',
        )
        try:
            dionysos_teilar_gr.save()
            status = 'NEW: %s from: %s' % (title, name)
            print status
            cronosDebug(status, logfile)
        except IntegrityError:
            pass
        except MySQLdb.Warning, warning:
            status = 'NEW: %s from %s' % (title, name)
            print status
            cronosDebug(status,logfile)
            warningstatus = 'WARNING: %s' % str(warning)
            print warningstatus
            cronosDebug(warningstatus, logfile)
            success = False
            pass
        except Exception as error:
            errorstatus = 'ERROR: %s %s' % (title, str(error))
            print errorstatus
            cronosDebug(errorstatus, logfile)
            success = False
            pass

def library_teilar_gr():
    b = StringIO.StringIO()
    conn.setopt(pycurl.URL, 'http://library.teilar.gr/news_gr.php')
    conn.setopt(pycurl.WRITEFUNCTION, b.write)
    conn.perform()
    output = unicode(b.getvalue(), 'utf-8', 'ignore')
    soup = BeautifulSoup(str(BeautifulSoup(output).findAll('table')[9]))

    for item in soup.findAll('a', 'BlackText11'):
        title = item.contents[0]
        link = 'http://library.teilar.gr/' +str(item).split('"')[1]

        b = StringIO.StringIO()
        conn.setopt(pycurl.URL, link)
        conn.setopt(pycurl.WRITEFUNCTION, b.write)
        conn.perform()
        output = unicode(b.getvalue(), 'utf-8', 'ignore')
        soup1 = BeautifulSoup(output)
        main_text = soup1.findAll('td', 'BlackText11')[2].contents[0]
        main_text = p.sub(' ', main_text)
        name = getid('cid', 54)
        
        library_teilar_gr = Announcements(
            title = title,
            url = link,
            urlid = name,
            description = main_text.strip(),
            unique = link,
            attachment_url = '',
            attachment_text = '',
        )
        try:
            library_teilar_gr.save()
            status = 'NEW: %s from: %s' % (title, name)
            print status
            cronosDebug(status, logfile)
        except IntegrityError:
            pass
        except MySQLdb.Warning, warning:
            status = 'NEW: %s from %s' % (title, name)
            print status
            cronosDebug(status,logfile)
            warningstatus = 'WARNING: %s' % str(warning)
            print warningstatus
            cronosDebug(warningstatus, logfile)
            success = False
            pass
        except Exception as error:
            errorstatus = 'ERROR: %s %s' % (title, str(error))
            print errorstatus
            cronosDebug(errorstatus, logfile)
            success = False
            pass

def pr_teilar_gr():
    link = ['general_news/', 'meeting_conference/']

    for item in link:
        b = StringIO.StringIO()
        conn.setopt(pycurl.URL, 'http://www.pr.teilar.gr/el/announcements/' + item)
        conn.setopt(pycurl.WRITEFUNCTION, b.write)
        conn.perform()
        output = unicode(b.getvalue(), 'utf-8', 'ignore')
        soup = BeautifulSoup(output)

        for item in soup.findAll('span','ba'):
            title = item.a.contents[0]
            link1 = 'http://www.pr.teilar.gr' + str(item.contents[0]).split('"')[1]
            
            b = StringIO.StringIO()
            conn.setopt(pycurl.URL, link1)
            conn.setopt(pycurl.WRITEFUNCTION, b.write)
            conn.perform()
            output = unicode(b.getvalue(), 'utf-8', 'ignore')
            soup1 = BeautifulSoup(output)

            main_text = ''
            for item1 in soup1.findAll('td', 'subject')[0].contents:
                main_text += str(item1)
            main_text = p.sub(' ', main_text)
            name = getid('cid', 55)

            pr_teilar_gr = Announcements(
                title = title,
                url = link1,
                urlid = name,
                description = main_text,
                unique = link1,
                attachment_url = '',
                attachment_text = '',
            )
            try:
                pr_teilar_gr.save()
                status = 'NEW: %s from: %s' % (title, name)
                print status
                cronosDebug(status, logfile)
            except IntegrityError:
                pass
            except MySQLdb.Warning, warning:
                status = 'NEW: %s from %s' % (title, name)
                print status
                cronosDebug(status,logfile)
                warningstatus = 'WARNING: %s' % str(warning)
                print warningstatus
                cronosDebug(warningstatus, logfile)
                success = False
                pass
            except Exception as error:
                errorstatus = 'ERROR: %s %s' % (title, str(error))
                print errorstatus
                cronosDebug(errorstatus, logfile)
                success = False
                pass

def main():
    cronosDebug('started', logfile)
    www_teilar_gr()
    cronosDebug('teilar finished', logfile)
    professors()
    cronosDebug('professors finished', logfile)
    eclass_teilar_gr()
    cronosDebug('eclass finished', logfile)
    noc_teilar_gr()
    cronosDebug('noc finished', logfile)
    career_teilar_gr()
    cronosDebug('career finished', logfile)
    linuxteam_cs_teilar_gr()
    cronosDebug('linuxteam finished', logfile)
    dionysos_teilar_gr()
    cronosDebug('dionysos finished', logfile)
    library_teilar_gr()
    cronosDebug('library finished', logfile)
    pr_teilar_gr()
    cronosDebug('pr finished', logfile)

    if success:
        cronosDebug('Announcements cron job finished successfully', logfile)
    else:
        cronosDebug('Announcements cron job finished but with Errors', logfile)
    print "DONE"

if __name__ == '__main__':
    main()
