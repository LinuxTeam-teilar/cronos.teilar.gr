from base64 import encodestring as encode
from Crypto.Cipher import Blowfish
from django.conf import settings
from random import choice
import base64
import hashlib
import os
import string

def sha1_password(password):
    '''
    NOT USED
    Create a sha1 hash in order to store a password encrypted in the DB
    '''
    salt = os.urandom(4)
    h = hashlib.sha1(password)
    h.update(salt)
    return "{SSHA}" + encode(h.digest() + salt)

def encrypt_password(password):
    '''
    Encrypt the password in Blowfish encryption, using the blowfish key
    specified in the settings file
    '''
    obj = Blowfish.new(settings.BLOWFISH_KEY)
    if len(str(len(password))) == 1:
        length = '0' + str(len(password))
    else:
        length = str(len(password))
    new_password = length + password
    if len(new_password) % 8 != 0:
        new_password += (''.join([choice(string.letters + string.digits) for i in range(8 - (len(new_password) % 8))]))
    return base64.b64encode(obj.encrypt(new_password))

def decrypt_password(password):
    '''
    Decrypt the password from Blowfish encryption, using the blowfish key
    specified in the settings file
    '''
    obj = Blowfish.new(settings.BLOWFISH_KEY)
    original_password = obj.decrypt(base64.b64decode(password))
    return original_password[2:int(original_password[:2]) + 2]
