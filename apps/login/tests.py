# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import Client
from apps.teilar.models import Departments

try:
    from apps.login.fixtures.all_real_accounts import all_real_accounts
    '''
    Get the first student
    '''
    first_student_username = list(all_real_accounts)[0]
    first_student_password = all_real_accounts[first_student_username]
    first_student = {
        'username': first_student_username,
        'password': first_student_password
    }
except ImportError:
    print 'WARNING: In order to run all the tests successfully, you need first
to run the following command in the production instance: \
\nsh /path/to/cronos/others/get_all_real_accounts.sh /path/to/cronos \
\nThis will create two files under /tmp/cronos/fixtures, which need to be \
copied in the testing instance under apps/login/fixtures'

class EmptyDBLoginTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_incorrect_user(self):
        '''
        Test if incorrect credentials show up the expected error message
        '''
        wrong_account = {
            'username': 'username',
            'password': 'password',
        }
        response = self.client.post('/login/', wrong_account)
        self.assertEqual(response.context['msg'], u'Λάθος στοιχεία')

    def test_no_matching_department(self):
        '''
        Test if a student with no matching department or with an emtpy database
        causes the expected error message to show up
        '''
        response = self.client.post('/login/', first_student)
        self.assertEqual(response.context['msg'], u'Σφάλμα αποθήκευσης πρόσθετων στοιχείων χρήστη')

class NewUserLoginTest(TestCase):
    fixtures = ['departments.json']

    def setUp(self):
        self.client = Client()

    def test_successful_login(self):
        '''
        Test if real students can login from dionysos successfully
        TODO: check if their data will be imported correctly in the DB
        '''
        for username, password in all_real_accounts.iteritems():
            student = {'username': username, 'password': password}
            response = self.client.post('/login/', student)
            self.assertEqual(response.status_code, 302)
#            self.assertEqual(response['Location'], 'http://testserver/')

class ExistingUserLoginTest(TestCase):
    fixtures = ['full_production_db.json']

    def setUp(self):
        self.client = Client()

    def test_successful_login(self):
        '''
        Test if a real student that is already in the DB can login
        successfully
        '''
        response = self.client.post('/login/', first_student)
        self.assertEqual(response.status_code, 302)
