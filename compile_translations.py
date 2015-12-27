#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Compile translations"""


import sys
from os import makedirs, walk
from os.path import basename, join, splitext
from subprocess import check_call


if len(sys.argv) != 3:
    print('Usage: %s <program-name> <po directory>' % sys.argv[0])
    sys.exit(0)

PO_DIR = sys.argv[-1]
PROGRAM = sys.argv[-2]

# PO_FILES = []
# for dirpath, dirnames, filenames in walk(PO_DIR):
#     for filename in filenames:
#         if filename.split('.')[-1] == 'po':
#             PO_FILES.append(join(dirpath, filename))

PO_FILES = [join(p, f) for p, d, files in walk(PO_DIR)
            for f in files if f.endswith('.po')]

for po in PO_FILES:
    lang = basename(po)
    print('Compiling for Locale: ' + ''.join(lang.split('.')[:-1]))
    lang = lang.split('-')[-1]
    lang = splitext(lang)[0]
    lang = lang.strip()
    if not lang:
        continue

    lang_lc_dir = join('share', 'locale', lang, 'LC_MESSAGES')
    makedirs(lang_lc_dir, exist_ok=True)

    check_call(['msgfmt', po, '-o', join(lang_lc_dir, PROGRAM + '.mo')])
