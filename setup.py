#!/usr/bin/env python

from distutils.core import setup
import os
import sys


def main():

    SHARE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
            "share")

    data_files = []
    
    # don't trash the users system icons!!
    black_list = ['index.theme', 'index.theme~']

    for path, dirs, files in os.walk(SHARE_PATH):

        data_files.append(tuple((path.replace(SHARE_PATH,"share", 1),
            [os.path.join(path, file) for file in files if file not in
                black_list])))

    ### UPDATE THIS INFORMATION
    setup(name="caffeine",
        version='0.1',
        description="",
        author="Isaiah Heyer",
        author_email="freshapplepy@gmail.com",
        url="https://launchpad.net/caffeine",
        packages=["caffeine"],
        data_files=data_files,
        scripts=[os.path.join("bin", "caffeine")]
        )

if __name__ == "__main__":
    main()
