#!/usr/bin/python3
# -*- coding: utf-8 -*-


from setuptools import setup
from os import chdir, makedirs, walk
from os.path import abspath, dirname, join, relpath
from shutil import copy
from subprocess import check_call


def read(path):
    with open(path) as f:
        return f.read().strip()


# identify and enter root directory
ROOT_DIR = dirname(abspath(__file__))
chdir(ROOT_DIR)

# update the translations
PO_DIR = 'translations'
makedirs(PO_DIR, exist_ok=True)
check_call(['xgettext', '-o', join(PO_DIR, 'caffeine-indicator.pot'),
            '--from-code=UTF-8', '--language=python', 'caffeine-indicator'])
check_call(['./compile_translations.py', 'caffeine-indicator', PO_DIR])

# don't trash the system icons!
BLACKLIST = ['index.theme']

SHARE_DIR = join(ROOT_DIR, 'share')

# # generate list of data files to include
# DATA_FILES = []
# for path, dirs, files in walk(SHARE_DIR):
#     DATA_FILES.append((relpath(path, ROOT_DIR),
#                        [join(path, f) for f in files if f not in BLACKLIST]))

# generate list of data files to include
DATA_FILES = [(relpath(p, ROOT_DIR), [join(p, f) for f in files if f not in BLACKLIST]) for p, d, files in walk(SHARE_DIR)]

# prepare caffeine-indicator.desktop for install to ./etc/xdg/autostart
DESKTOP_NAME = 'caffeine-indicator.desktop'
DESKTOP_FILE = join('share', 'applications', DESKTOP_NAME)
AUTOSTART_DIR = join('etc', 'xdg', 'autostart')
makedirs(AUTOSTART_DIR, exist_ok=True)
copy(DESKTOP_FILE, AUTOSTART_DIR)
DATA_FILES.append((('/' + AUTOSTART_DIR, [join(AUTOSTART_DIR, DESKTOP_NAME)])))

setup(
    name='caffeine-reloaded',
    version=read('VERSION'),
    description='Stop the desktop from becoming idle in full-screen mode.',
    author='Brian Beffa',
    author_email='brbsix@gmail.com',
    url='https://github.com/brbsix/caffeine-reloaded',
    license='GPLv3',
    py_modules=['ewmh'],
    install_requires=['python-xlib'],
    data_files=DATA_FILES,
    scripts=[
        'caffeine',
        'caffeinate',
        'caffeine-indicator',
        'caffeine-screensaver',
        'caffeine-screensaver-freedesktop-helper'
        ]
)
