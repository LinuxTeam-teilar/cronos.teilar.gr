# -*- coding: utf-8 -*-

import os
import sys
sys.path.append(sys.argv[1])
os.environ['DJANGO_SETTINGS_MODULE'] = 'cronos.settings'
from cronos.accounts.models import UserProfile
from cronos.accounts.encryption import decrypt_password

all_students = {}
all_students_q = UserProfile.objects.filter(deprecated = False)
for student in all_students_q:
    all_students[student.dionysos_username] = decrypt_password(student.dionysos_password)

print 'all_real_accounts = ' + str(all_students)
