# -*- coding: utf-8 -*-

from cronos.common.encryption import decrypt_password
from cronos.common.get_admins import get_admins_usernames
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        all_students = {}
        admins = get_admins_usernames()
        all_students_q = User.objects.filter(is_active = True).exclude(username_in = admins)
        for student in all_students_q:
            all_students[student.get_profile().dionysos_username] = decrypt_password(student.get_profile().dionysos_password)

        self.stdout.write('all_real_accounts = %s\n' % str(all_students))
