#!/usr/bin/python
# -*- coding: utf-8 -*-

### BEGIN LICENSE
# Copyright (C) 2013 <Janez Troha> <dz0ny@shortmail.com>
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License version 3, as published 
# by the Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranties of 
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR 
# PURPOSE.  See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along 
# with this program.  If not, see <http://www.gnu.org/licenses/>.
### END LICENSE

from gi.repository import Gtk, Gdk, WebKit, Soup  # pylint: disable=E0611
import json
import os
import sys
import logging
import subprocess
logger = logging.getLogger('ubuntu_si_welcome')

from ubuntu_si_welcome_lib import get_data_path
from ubuntu_si_welcome_lib import xdg_data_home


class Okno(Gtk.Window):

    def __init__(self, width, height):

        # create the window

        Gtk.Window.__init__(self)
        splitter = Gtk.Paned(orientation=Gtk.Orientation.VERTICAL)
        splitter.show()

        # create the widget container

        vbox = Gtk.VBox(homogeneous=False)
        self.add(splitter)
        vbox.show()
        splitter.add1(vbox)

        # create the menu

        file_menu = Gtk.Menu()

        accel_group = Gtk.AccelGroup()
        self.add_accel_group(accel_group)

        quit_item = Gtk.MenuItem()
        quit_item.set_label('_Quit')
        quit_item.set_use_underline(True)
        accel = Gtk.accelerator_parse('<Control>q')
        quit_item.add_accelerator('activate', accel_group, accel[0], accel[1],
                                  Gtk.AccelFlags.VISIBLE)
        quit_item.show()
        quit_item.connect('activate', self.quit)
        file_menu.append(quit_item)
        quit_item.show()

        menu_bar = Gtk.MenuBar()
        vbox.pack_start(menu_bar, False, False, 0)
        menu_bar.show()

        file_item = Gtk.MenuItem()
        file_item.set_label('_File')
        file_item.set_use_underline(True)
        file_item.show()

        file_item.set_submenu(file_menu)
        menu_bar.append(file_item)

        #Settings

        #self.settings = Settings("com.dz0ny.ubuntu-si-welcome")

        # create the WebView

        self.scroller = Gtk.ScrolledWindow()

        # Enables Cookies

        session = WebKit.get_default_session()
        cache = os.path.join(xdg_data_home(), 'com.dz0ny.ubuntu-si-welcome')
        cookie_jar = Soup.CookieJarText.new(os.path.join(cache, 'WebkitSession'), False)
        session.add_feature(cookie_jar)
        session.props.max_conns_per_host = 8

        self.webview = WebKit.WebView()
        self.scroller.add(self.webview)
        self.webview.props.settings.enable_default_context_menu = False

        settings = self.webview.get_settings()
        settings.set_property("enable-plugins", False)
        settings.set_property('javascript-can-open-windows-automatically', True)
        settings.set_property('enable-universal-access-from-file-uris', True)
        settings.set_property('enable-developer-extras', False)

        self.webview_inspector = self.webview.get_inspector()
        self.webview_inspector.connect('inspect-web-view', self.inspect_webview)
        self.inspector_window = Gtk.Window()

        self.webview.show()
        self.scroller.show()

        # and use that for sizing

        self.set_size_request(width, height)

        # add the webkit window

        vbox.pack_start(self.scroller, True, True, 0)

        self.webview.connect("navigation-policy-decision-requested", self._on_new_window)
        #self.webview.connect("console-message", self._on_console_message)

        # a possible way to do IPC (script or title change)
        self.webview.connect("script-alert", self._on_script_alert)
        self.webview.connect("title-changed", self._on_title_changed)

        html_file = """%s/web_app/public/index.html""" % get_data_path()
        self.webview.open(html_file)

    def inspect_webview(
        self,
        inspector,
        widget,
        data=None,
    ):

        inspector_view = WebKit.WebView()
        self.inspector_window.add(inspector_view)
        self.inspector_window.resize(800, 400)
        self.inspector_window.show_all()
        self.inspector_window.present()
        return inspector_view

    def _on_new_window(self, web_view, frame, request, navigation_action, policy_decision):
        #print "_on_new_window", web_view, frame, request, navigation_action, policy_decision
        #policy_decision.webkit_web_policy_decision_ignore()
        rui = request.get_uri()
        if "file://" in rui or "webchat" in rui or "about:" in rui:
            return False
        else:
            policy_decision.ignore()
            print request.get_uri()
            subprocess.Popen(['xdg-open', request.get_uri()])
            return True

    def _on_console_message(self, view, message, line, source_id):
        print "_on_console_message", message, line, source_id
        return False

    def _on_script_alert(self, view, frame, message):
        # stop further processing to avoid actually showing the alter
        #print "_on_script_alert", view, frame, messag
        return True

    def _on_title_changed(self, view, frame, title):
        #print "on_title_changed", view, frame, title
        self.set_title(title)
        # see wkwidget.py _on_title_changed() for a code example

    def quit(self, widget, data=None):
        self.destroy()
