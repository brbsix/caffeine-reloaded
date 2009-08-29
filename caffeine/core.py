#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2009 The Caffeine Developers
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import gtk
import gobject
import os
import pynotify
import commands

import dbus
import threading

import applicationinstance

import caffeine
import utils
import procmanager

class Caffeine(gobject.GObject):

    def __init__(self):
        
        gobject.GObject.__init__(self)
        
        ## convience class for managing configurations
        self.Conf = caffeine.get_configurator()

        ## object to manage processes to activate for.
        self.ProcMan = caffeine.get_ProcManager()
        
        ## Makes sure that only one instance of Caffeine is run for
        ## each user on the system.
        self.pid_name = '/tmp/caffeine' + str(os.getuid()) + '.pid'
        self.appInstance = applicationinstance.ApplicationInstance( self.pid_name )

        ## This variable is set to a string describing the type of screensaver and
        ## powersaving systems used on this computer. It is detected when the user
        ## first attempts to inhibit the screensaver and powersaving, and can be set
        ## to one of the following values: "Gnome", "KDE", "XSS+DPMS" or "DPMS".
        self.screensaverAndPowersavingType = None

        # Set to True when the detection routine is in progress
        self.attemptingToDetect = False

        self.dbusDetectionTimer = None
        self.dbusDetectionFailures = 0

        # Set to True when sleep seems to be prevented from the perspective of the user.
        # This does not necessarily mean that sleep really is prevented, because the
        # detection routine could be in progress.
        self.sleepAppearsPrevented = False

        # Set to True when sleep mode has been successfully inhibited somehow. This should
        # match up with "self.sleepAppearsPrevented" most of the time.
        self.sleepIsPrevented = False
        self.preventedForProcess = False

        self.screenSaverCookie = None
        self.powerManagementCookie = None
        self.timer = None
        self.inhibit_id = None


        self.note = None
        
        ## check for processes to activate for.
        id = gobject.timeout_add(5000, self.check_for_process)

    def check_for_process(self):
        print self.preventedForProcess
        activate = False
        for proc in self.ProcMan.get_process_list():
            if utils.isProcessRunning(proc):
                activate = True
                if not self.getActivated():
                    self.toggleActivated()

                self.preventedForProcess = True

        if not activate and self.preventedForProcess:
            if self.getActivated():
                self.toggleActivated()

        return True

    def quit(self):
        """Cancels any timer thread running
        so the program can quit right away.
        """
        if self.timer:
            self.timer.cancel()

        if self.dbusDetectionTimer:
            self.dbusDetectionTimer.cancel()

    ## The following four methods deal with adding the correct syntax
    ## for plural forms of time units. For example, 1 minute and 2
    ## minutes. Will be obsolete once the application is
    ## internationalized, as not all languages use "s" for plural form.
    def _mconcat(self, base, sep, app):
        return (base + sep + app if base else app) if app else base

    def _spokenConcat(self, ls):
        and_str = _(" and ")
        txt, n = '', len(ls)
        for w in ls[0:n-1]:
            txt = self._mconcat(txt, ', ', w)
        return self._mconcat(txt, and_str, ls[n-1])

    def _pluralize(self, name, time):
        names = [_('hour'), _('minute')]
        if time < 1:
            return ""

        if name == "hour":
            if time < 2:
                return "%d %s" % (time, _("hour"))
            if time >= 2:
                return "%d %s" % (time, _("hours"))

        elif name == "minute":
            if time < 2:
                return "%d %s" % (time, _("minute"))
            if time >= 2:
                return "%d %s" % (time, _("minutes"))

    def _timeDisplay(self, sec):

        hours = sec/3600
        minutes = sec/60 % 60
        ls = []
        ls.append(self._pluralize("hour", hours))
        ls.append(self._pluralize("minute", minutes))

        return self._spokenConcat(ls)


    def _notify(self, message, icon, title="Caffeine"):
        """Easy way to use pynotify"""
        try:

            pynotify.init("Caffeine")
            if self.note:
                self.note.update(title, message, icon)
            else:
                self.note = pynotify.Notification(title, message, icon)
            
            ## Notify OSD doesn't seem to work when sleep is prevented
            if self.screenSaverCookie != None and self.sleepIsPrevented:
                self.ssProxy.UnInhibit(self.screenSaverCookie)

            self.note.show()

            if self.screenSaverCookie != None and self.sleepIsPrevented:
                self.screenSaverCookie = self.ssProxy.Inhibit("Caffeine",
               "User has requested that Caffeine disable the screen saver")

        except Exception, e:
            print _("Exception occurred") + " " + str(e)
            print message
        finally:
            return False


    def getActivated(self):
        return self.sleepAppearsPrevented

    def timedActivation(self, time):
        """Calls toggleActivated after the number of seconds
        specified by time has passed.
        """
        message = (_("Timed activation set; ")+
            _("Caffeine will prevent powersaving for the next ") +
            self._timeDisplay(time))
        print "Timed activation set for " + self._timeDisplay(time)

        if not self.getActivated():
            self.toggleActivated()


        self._notify(message, caffeine.FULL_ICON_PATH)

        ## and deactivate after time has passed.
        ## Stop already running timer
        if self.timer:
            self.timer.cancel()

        self.timer = threading.Timer(time, self._deactivate)
        self.timer.name = "Active"
        self.timer.start()

    
    def _deactivate(self):
        self.timer.name = "Expired"
        self.toggleActivated()


    def toggleActivated(self):
        """This function toggles the inhibition of the screensaver and powersaving
        features of the current computer, detecting the the type of screensaver and powersaving
        in use, if it has not been detected already."""

        if self.preventedForProcess:
            self.preventedForProcess = False

        if self.sleepAppearsPrevented:
            ### sleep prevention was on now turn it off

            self.sleepAppearsPrevented = False
            print "Caffeine is now dormant; powersaving is re-enabled"

            # If the user clicks on the full coffee-cup to disable
            # sleep prevention, it should also
            # cancel the timer for timed activation.

            if self.timer != None and self.timer.name != "Expired":

                message = (_("Timed activation cancelled (was set for ") +
                        self._timeDisplay(self.timer.interval) + ")")
                print "Timed activation cancelled"

                self._notify(message, caffeine.EMPTY_ICON_PATH)

                self.timer.cancel()
                self.timer = None

                

            elif self.timer != None and self.timer.name == "Expired":

                message = (self._timeDisplay(self.timer.interval) +
                    _(" have elapsed; powersaving is re-enabled"))
                print "Timed activation period has elapsed"

                self._notify(message, caffeine.EMPTY_ICON_PATH)

                self.timer = None

        else:

            self.sleepAppearsPrevented = True

        self.emit("activation-toggled", self.getActivated())
        self._performTogglingActions()

    def _detectScreensaverAndPowersavingType(self):
        """This method always runs when the first attempt to inhibit the screensaver and
        powersaving is made. It detects what screensaver/powersaving software is running.
        After detection is complete, it will finish the inhibiting process."""
        print ("Attempting to detect screensaver/powersaving type... (" + str(self.dbusDetectionFailures) + " dbus failures so far)")
        bus = dbus.SessionBus()
        if 'org.gnome.ScreenSaver' in bus.list_names():
            self.screensaverAndPowersavingType = "Gnome"
        elif 'org.freedesktop.ScreenSaver' in bus.list_names() and \
             'org.freedesktop.PowerManagement.Inhibit' in bus.list_names():
            self.screensaverAndPowersavingType = "KDE"
        else:
            self.dbusDetectionFailures += 1
            if self.dbusDetectionFailures <= 8:
                self.dbusDetectionTimer = threading.Timer(15, self._detectScreensaverAndPowersavingType)
                self.dbusDetectionTimer.start()
                return
            else:
                # At this point, all attempts to connect to the relevant dbus interfaces have failed.
                # This user must be using something other than the Gnome or KDE screensaver programs.
                if utils.isProcessRunning("xscreensaver"):
                    self.screensaverAndPowersavingType = "XSS+DPMS"
                else:
                    self.screensaverAndPowersavingType = "DPMS"

        self.attemptingToDetect = False
        self.dbusDetectionFailures = 0
        self.dbusDetectionTimer = None
        print ("Successfully detected screensaver and powersaving type: " + str(self.screensaverAndPowersavingType))
        if self.sleepAppearsPrevented != self.sleepIsPrevented:
            self._performTogglingActions()

    def _performTogglingActions(self):
        """This method performs the actions that affect the screensaver and
        powersaving."""
        if self.screensaverAndPowersavingType == None:
            if self.attemptingToDetect == False:
                self.attemptingToDetect = True
                self._detectScreensaverAndPowersavingType()
            return

        if self.screensaverAndPowersavingType == "Gnome":
            self._toggleGnome()
        elif self.screensaverAndPowersavingType == "KDE":
            self._toggleKDE()
        elif self.screensaverAndPowersavingType == "XSS+DPMS":
            self._toggleXSSAndDPMS()
        elif self.screensaverAndPowersavingType == "DPMS":
            self._toggleDPMS()

        if self.sleepIsPrevented == False:
            print ("Caffeine is now preventing powersaving modes"+
                " and screensaver activation (" +
                self.screensaverAndPowersavingType + ")")

        self.sleepIsPrevented = not self.sleepIsPrevented

    def _toggleGnome(self):
        """Toggle the screensaver and powersaving with the interfaces used by Gnome."""

        bus = dbus.SessionBus()
        self.ssProxy = bus.get_object('org.gnome.ScreenSaver',
                    '/org/gnome/ScreenSaver')
        if self.sleepIsPrevented:
            if self.screenSaverCookie != None:
                self.ssProxy.UnInhibit(self.screenSaverCookie)
        else:
            self.screenSaverCookie = self.ssProxy.Inhibit("Caffeine",
                    "User has requested that Caffeine disable the screen saver")

    def _toggleKDE(self):
        """Toggle the screensaver and powersaving with the interfaces used by KDE."""

        self._toggleDPMS()
        bus = dbus.SessionBus()
        self.ssProxy = bus.get_object(
                'org.freedesktop.ScreenSaver', '/ScreenSaver')
        pmProxy = bus.get_object(
                'org.freedesktop.PowerManagement.Inhibit',
                '/org/freedesktop/PowerManagement/Inhibit')
        if self.sleepIsPrevented:
            if self.screenSaverCookie != None:
                self.ssProxy.UnInhibit(self.screenSaverCookie)
            if self.powerManagementCookie != None:
                pmProxy.UnInhibit(self.powerManagementCookie)
        else:
            self.powerManagementCookie = pmProxy.Inhibit("Caffeine",
                    "User has requested that Caffeine disable"+
                    " the powersaving modes")
            self.screenSaverCookie = self.ssProxy.Inhibit("Caffeine",
                    "User has requested that Caffeine disable the screen saver")

    def _toggleXSSAndDPMS(self):
        self._toggleXSS()
        self._toggleDPMS()

    def _toggleDPMS(self):
        """Toggle the DPMS powersaving subsystem."""
        if self.sleepIsPrevented:
            commands.getoutput("xset +dpms")
        else:
            commands.getoutput("xset -dpms")

    def _toggleXSS(self):
        """Toggle whether XScreensaver is activated (powersaving is unaffected)"""

        if self.sleepIsPrevented:
            ### sleep prevention was on now turn it off

            # If the user clicks on the full coffee-cup to disable
            # sleep prevention, it should also
            # cancel the timer for timed activation.

            if self.inhibit_id != None:
                gobject.source_remove(self.inhibit_id)

        else:

            def deactivate():
                try:
                    output = commands.getoutput(
                            "xscreensaver-command -deactivate")
                except Exception, data:
                    print data

                return True
        
            # reset the idle timer every 50 seconds.
            self.inhibit_id = gobject.timeout_add(50000, deactivate)

        self.emit("activation-toggled", self.getActivated())



## register a signal
gobject.signal_new("activation-toggled", Caffeine,
        gobject.SIGNAL_RUN_FIRST, None, [bool])


