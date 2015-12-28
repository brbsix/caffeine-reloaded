About
=====

**caffeine-reloaded** is an almost complete rewrite of lp:caffeine_
It was created in an effort to tidy up the code, increase stability,
and add additional features.

The prime directive is to prevent the screen saver from activating
when desired. This can be achieved automatically (detecting when the
active window is fullscreen) or via manual toggle.


Installation
============

**caffeine-reloaded** is available for installation solely via *.deb*.

To download, visit `latest release`_ or run the following command:

::

  curl --remote-name -sL https://github.com/brbsix/caffeine-reloaded/releases/download/v0.0.2/caffeine-reloaded_0.0.2_all.deb

To install with :code:`apt` and :code:`dpkg`:

::

  sudo dpkg --install caffeine-reloaded_0.0.2_all.deb
  sudo apt-get install --fix-broken  # to resolve any missing dependencies

To install with :code:`gdebi`:

::

  sudo gdebi ./caffeine-reloaded_0.0.2_all.deb

To install with :code:`gdebi-gtk`:

::

  gdebi-gtk ./caffeine-reloaded_0.0.2_all.deb


Development
===========

To build **caffeine-reloaded** into a *.deb* youself, run the following from package's root directory:

::

  # increment changelog (assuming you have updated VERSION)
  dch --controlmaint --distribution vivid --newversion "$(< VERSION)" --urgency low

  # build
  debuild -b -uc -us

If :code:`debuild` reports missing build dependencies, just install them and retry.


Usage
=====

**caffeinate** allows desktop idleness to be inhibited for the duration
for any command.

::

  caffeinate COMMAND

**caffeine** is a small daemon that prevents desktop idleness while the
active window is fullscreen.

::

  usage: caffeine [OPTION]...

  optional arguments:
    -q, --quiet      suppress normal output
    -t, --timestamp  timestamp log entries
    -V, --version    show program's version number and exit

**caffeine-indicator** is a GUI status bar indicator that can be used to
toggle desktop idleness inhibition. By default, it manually inhibits and
uninhibits desktop idleness. However with the :code:`--auto` option, it
behaves like :code:`caffeine` and prevents desktop idleness only while the
active window is fullscreen.

::

  usage: caffeine-indicator [OPTION]...

  optional arguments:
    -a, --auto       prevent desktop idleness in fullscreen mode
    -q, --quiet      suppress normal output
    -t, --timestamp  timestamp log entries
    -V, --version    show program's version number and exit


Translations
============

Please note that I've made significant changes from caffeine 2.8.3.
Translations have not been correspondingly updated.

If you want to test out a translation without changing the language for the
whole session, run caffeine as e.g.: :code:`LANGUAGE=ru ./caffeine`

To compile the translations: :code:`./update_translations.py` (this is done
automatically when building the package, so no need to do it normally).

You will need a language pack for the given language. Be aware that some
stock items will not be translated unless you log in with a given language.


License
=======

Created by Reuben Thomas <rrt@sc3d.org>

Forked by Brian Beffa <brbsix@gmail.com>

caffeine-reloaded is distributed under the GNU General Public License,
either version 3, or (at your option) any later version. See COPYING.

The Caffeine SVG icons are Copyright (c) 2009 Tommy Brunn
(http://www.blastfromthepast.se/blabbermouth), and distributed under the
terms of the GNU Lesser General Public License, either version 3, or (at
your option) any later version. See COPYING.LESSER.

caffeine-reloaded uses pyewmh from http://sf.net/projects/pyewmh

.. _lp:caffeine: http://launchpad.net/caffeine
.. _latest release: https://github.com/brbsix/caffeine-reloaded/releases/latest
