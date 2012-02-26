# -*- coding: utf-8 -*-

def sha1Password(password):
    from base64 import encodestring as encode
    import base64
    import hashlib
    import os

    salt = os.urandom(4)
    h = hashlib.sha1(password)
    h.update(salt)
    return "{SSHA}" + encode(h.digest() + salt)

def encryptPassword(password):
    from Crypto.Cipher import Blowfish
    from django.conf import settings
    from random import choice
    import base64
    import string

    obj = Blowfish.new(settings.BLOWFISH_KEY)
    if len(str(len(password))) == 1:
        length = '0' + str(len(password))
    else:
        length = str(len(password))
    new_password = length + password
    if len(new_password) % 8 != 0:
        new_password += (''.join([choice(string.letters + string.digits) for i in range(8 - (len(new_password) % 8))]))
    return base64.b64encode(obj.encrypt(new_password))

def decryptPassword(password):
    from Crypto.Cipher import Blowfish
    from django.conf import settings
    from random import choice
    import base64
    
    obj = Blowfish.new(settings.BLOWFISH_KEY)
    original_password = obj.decrypt(base64.b64decode(password))
    return original_password[2:int(original_password[:2]) + 2]
    return original_password
