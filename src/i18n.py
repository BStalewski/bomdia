# -*- coding: utf-8 -*-

# Based on code from http://wiki.maemo.org/Internationalize_a_Python_application

import gettext
import locale
import os


APP_NAME = 'Bomdia'
APP_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
LOCALE_DIR = os.path.join(APP_DIR, 'i18n')

DEFAULT_LANGUAGES = os.environ.get('LANG', '').split(':')
DEFAULT_LANGUAGES = ['en_US']

lc, encoding = locale.getdefaultlocale()
if lc:
    languages = [lc]

languages += DEFAULT_LANGUAGES
mo_location = LOCALE_DIR

gettext.install(True, localedir=None, unicode=1)
gettext.find(APP_NAME, mo_location)
gettext.textdomain(APP_NAME)
gettext.bind_textdomain_codeset(APP_NAME, 'UTF-8')

language = gettext.translation(APP_NAME, mo_location, languages=languages, fallback=True)
