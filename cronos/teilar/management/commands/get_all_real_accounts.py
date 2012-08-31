# -*- coding: utf-8 -*-

from cronos.accounts.models import UserProfile
from cronos.common.encryption import decrypt_password
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        all_students = {}
        all_students_q = UserProfile.objects.filter(deprecated = False)
        for student in all_students_q:
            all_students[student.dionysos_username] = decrypt_password(student.dionysos_password)

        self.stdout.write('all_real_accounts = %s\n' % str(all_students))
