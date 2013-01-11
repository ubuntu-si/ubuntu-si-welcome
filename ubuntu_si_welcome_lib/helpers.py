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

### DO NOT EDIT THIS FILE ###

"""Helpers for an Ubuntu application."""

import logging
import os
import sys

from ubuntu_si_welcomeconfig import get_data_file

from locale import gettext as _


def expandvarsu(path):
    """ Unicode version of os.path.expandvars """

    return unicode(os.path.expandvars(path), sys.getdefaultencoding())


def getenvu(key, default=None):
    """ Unicode version of os.getenv """

    var = os.getenv(key, default)
    return (var if isinstance(var, unicode) else unicode(var, sys.getdefaultencoding()))


def xdg_config_home():
    return getenvu('XDG_CONFIG_HOME', expandvarsu('$HOME/.config'))


def xdg_data_home():
    return getenvu('XDG_DATA_HOME', expandvarsu('$HOME/.cache'))


# Owais Lone : To get quick access to icons and stuff.

def get_media_file(media_file_name):
    media_filename = get_data_file('media', '%s' % (media_file_name, ))
    if not os.path.exists(media_filename):
        media_filename = None

    return 'file:///' + media_filename


class NullHandler(logging.Handler):

    def emit(self, record):
        pass


def set_up_logging(opts):

    # add a handler to prevent basicConfig

    root = logging.getLogger()
    null_handler = NullHandler()
    root.addHandler(null_handler)

    formatter = logging.Formatter("%(levelname)s:%(name)s: %(funcName)s() '%(message)s'")

    logger = logging.getLogger('ubuntu_si_welcome')
    logger_sh = logging.StreamHandler()
    logger_sh.setFormatter(formatter)
    logger.addHandler(logger_sh)

    lib_logger = logging.getLogger('ubuntu_si_welcome_lib')
    lib_logger_sh = logging.StreamHandler()
    lib_logger_sh.setFormatter(formatter)
    lib_logger.addHandler(lib_logger_sh)

    # Set the logging level to show debug messages.

    if opts.verbose:
        logger.setLevel(logging.DEBUG)
        logger.debug('logging enabled')
    if opts.verbose > 1:
        lib_logger.setLevel(logging.DEBUG)


def get_help_uri(page=None):

    # help_uri from source tree - default language

    here = os.path.dirname(__file__)
    help_uri = os.path.abspath(os.path.join(here, '..', 'help', 'C'))

    if not os.path.exists(help_uri):

        # installed so use gnome help tree - user's language

        help_uri = 'ubuntu-si-welcome'

    # unspecified page is the index.page

    if page is not None:
        help_uri = '%s#%s' % (help_uri, page)

    return help_uri


def show_uri(parent, link):
    from gi.repository import Gtk  # pylint: disable=E0611
    screen = parent.get_screen()
    Gtk.show_uri(screen, link, Gtk.get_current_event_time())


def alias(alternative_function_name):
    '''see http://www.drdobbs.com/web-development/184406073#l9'''

    def decorator(function):
        '''attach alternative_function_name(s) to function'''

        if not hasattr(function, 'aliases'):
            function.aliases = []
        function.aliases.append(alternative_function_name)
        return function

    return decorator
