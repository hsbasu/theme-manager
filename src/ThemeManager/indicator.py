# Copyright (C) 2021-2024 Himadri Sekhar Basu <hsb10@iitbbs.ac.in>
#
# This file is part of theme-manager.
#
# theme-manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# theme-manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with theme-manager. If not, see <http://www.gnu.org/licenses/>
# or write to the Free Software Foundation, Inc., 51 Franklin Street,
# Fifth Floor, Boston, MA 02110-1301, USA..
#
# Author: Himadri Sekhar Basu <hsb10@iitbbs.ac.in>
#

# import the necessary modules!
import gettext
import locale
import logging

# third-party library
import gi
gi.require_version('AppIndicator3', '0.1')
from gi.repository import AppIndicator3
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# imports from current package
from ThemeManager.about_window import AboutWindow
from ThemeManager.logger import LoggerWindow
from ThemeManager.cli_args import APP, LOCALE_DIR
from ThemeManager.common import theme_styles
from ThemeManager.tm_daemon import TMState_monitor
from ThemeManager.DesktopTheme import desktop_theme


# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# logger
module_logger = logging.getLogger('ThemeManager.indicator')

class TMIndicator():
	"""Class for system tray icon.
	
	This class will show Theme Manager icon in system tray.
	"""
	def __init__(self):
		module_logger.debug("Initiaing Appindicator.")
		self.indicator = AppIndicator3.Indicator.new(APP, APP, AppIndicator3.IndicatorCategory.SYSTEM_SERVICES)
		self.indicator.set_title(_('Theme Manager'))
		self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
		
		self.destop_manager = desktop_theme()
		self.daemon = TMState_monitor()
		self.theme_styles = theme_styles
		self.daemon.startdaemons()
		
		# create menu
		self.indicator.set_menu(self.__create_menu())
		Gtk.main()
	
	def __create_menu(self):
		menu = Gtk.Menu()
		
		# Add "Next Theme" option in drop-down menu
		item_next_theme = Gtk.ImageMenuItem(_('Next Theme'))
		item_next_theme.set_image(Gtk.Image.new_from_icon_name("next", Gtk.IconSize.MENU))
		item_next_theme.connect("activate", self.next_theme)
		menu.append(item_next_theme)
		
		# Add "Show Logs" option in drop-down menu
		item_show_log = Gtk.ImageMenuItem(_('Show Logs'))
		item_show_log.set_image(Gtk.Image.new_from_icon_name("text-x-log", Gtk.IconSize.MENU))
		item_show_log.connect("activate", self.show_logs, Gtk.Window())
		menu.append(item_show_log)
		
		# Add "About" option in drop-down menu
		item_about = Gtk.ImageMenuItem(_('About'))
		item_about.set_image(Gtk.Image.new_from_icon_name("help-about-symbolic", Gtk.IconSize.MENU))
		item_about.connect("activate", self.open_about, Gtk.Window())
		menu.append(item_about)
		
		# Add "Quit" option in drop-down menu
		item_quit = Gtk.ImageMenuItem(_('Quit'))
		item_quit.set_image(Gtk.Image.new_from_icon_name("stock_close", Gtk.IconSize.MENU))
		item_quit.connect("activate", self.__quit)
		menu.append(item_quit)
		
		menu.show_all()
		
		return menu
	
	def next_theme(self, *args):
		module_logger.info("User requested change using Next button from indicator.")
		self.state = self.daemon.manager.get_state_info()
		self.nexttheme = self.daemon.manager.prep_theme_variants(self.state, self.theme_styles)
		self.daemon.destop_manager.set_desktop_theme(self.state, self.nexttheme)
	
	def show_logs(self, signal, widget):
		loggerwindow = LoggerWindow(widget)
		loggerwindow.show()
	
	def open_about(self, signal, widget):
		about_window = AboutWindow(widget)
		about_window.show()
	
	def __quit(self, *args):
		Gtk.main_quit()
