#!/usr/bin/env python
# -*- coding: utf-8 -*-


import cStringIO


COLOR_INFO = '\033[94m'
COLOR_WARNING = '\033[93m'
COLOR_OK = '\033[92m'
COLOR_ERROR = '\033[91m'
COLOR_ENDING = '\033[0m'


def print_info(text):
    print COLOR_INFO + text + COLOR_ENDING


def print_ok(text):
    print COLOR_OK + text + COLOR_ENDING


def print_warning(text):
    print COLOR_WARNING + text + COLOR_ENDING


def print_error(text):
    print COLOR_ERROR + text + COLOR_ENDING


def get_fake_file(lines):
    output = cStringIO.StringIO()
    for line in lines:
        ended_line = line if line.endswith('\n') else line + '\n'
        output.write(ended_line)

    output.seek(0)
    return output
