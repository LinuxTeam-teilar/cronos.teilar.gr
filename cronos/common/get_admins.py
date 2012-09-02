from django.conf import settings

def get_admins_usernames():
    admins_usernames = []
    for admin in settings.ADMINS:
        admins_usernames.append(admin[0])
    return admins_usernames

def get_admins_mails():
    admins_mails = []
    for admin in settings.ADMINS:
        admins_mails.append(admin[1])
    return admins_mails
