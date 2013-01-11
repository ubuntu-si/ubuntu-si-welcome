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

from gi.repository import Gtk, Gdk, WebKit, Notify, Soup  # pylint: disable=E0611
import json
import os
import sys
import logging
logger = logging.getLogger('ubuntu_si_welcome')

from ubuntu_si_welcome_lib import get_data_path
from ubuntu_si_welcome_lib import xdg_data_home

try:
    from gi.repository import Unity, Dbusmenu
except ImportError:
    pass


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
        self.webviewsettings = self.webview.get_settings()
        self.webviewsettings.set_property('javascript-can-open-windows-automatically', True)
        self.webviewsettings.set_property('enable-universal-access-from-file-uris', True)
        self.webviewsettings.set_property('enable-developer-extras', True)

        self.webview_inspector = self.webview.get_inspector()
        self.webview_inspector.connect('inspect-web-view', self.inspect_webview)
        self.inspector_window = Gtk.Window()

        self.webview.show()
        self.scroller.show()

        # and use that for sizing

        self.set_size_request(width, height)

        # add the webkit window

        vbox.pack_start(self.scroller, True, True, 0)

        html_file = """%s/web_app/public/index.html""" % get_data_path()

        self.webview.open(html_file)

        self.webview.connect('title-changed', self._on_html_message)

        # Unity Support

        Notify.init('ubuntu-si-welcome')
        self.notification = Notify.Notification.new('ubuntu-si-welcome', '',
                '/usr/share/icons/hicolor/128x128/apps/ubuntu-si-welcome.png')
        try:
            launcher = Unity.LauncherEntry.get_for_desktop_id('ubuntu-si-welcome.desktop')

            ql = Dbusmenu.Menuitem.new()
            updatenews = Dbusmenu.Menuitem.new()
            updatenews.property_set(Dbusmenu.MENUITEM_PROP_LABEL, 'Link1')
            updatenews.property_set_bool(Dbusmenu.MENUITEM_PROP_VISIBLE, True)
            ql.child_append(updatenews)
            launcher.set_property('quicklist', ql)
        except NameError:
            pass

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

    def _on_html_message(
        self,
        view,
        frame,
        title,
        ):

        if title == 'null':

            # ignore when the title was set to null
            # typically to ensure the same message can be passed twice

            return
        else:
            try:
                message = json.loads(title)
            except Exception, inst:
                print inst
                message = {'signal': 'error', 'data': 'signal not parsed'}

        # self.on_html_message(message['signal'], message['data'])

    def send_html_message(self, signal, data):
        data_string = json.dumps(data)
        self.webview.execute_script("require('lib/backend')._receive_message('%s','%s');"
                                    % (signal, data_string))

    def quit(self, widget, data=None):
        self.destroy()
