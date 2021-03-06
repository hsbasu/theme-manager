# Copyright (C) 2021-2022 Himadri Sekhar Basu <hsb10@iitbbs.ac.in>
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
import gi
import locale
import logging
import setproctitle
import warnings

# Suppress GTK deprecation warnings
warnings.filterwarnings("ignore")

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gio

from ThemeManager.common import APP, CONFIG_FILE, LOCALE_DIR, UI_PATH, __version__, _async, TMBackend
from ThemeManager.indicator import TMIndicator
from ThemeManager.DesktopTheme import desktop_theme
# from ThemeManager.LoginTheme import login_theme

setproctitle.setproctitle(APP)

# i18n
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# logger
module_logger = logging.getLogger('ThemeManager.gui')


class theme_manager(Gtk.Application):
	# Main initialization routine
	def __init__(self, application_id, flags):
		Gtk.Application.__init__(self, application_id=application_id, flags=flags)
		self.connect("activate", self.activate)
	
	def activate(self, application):
		windows = self.get_windows()
		if (len(windows) > 0):
			window = windows[0]
			window.present()
			window.show()
		else:
			window = ThemeManagerWindow(self)
			self.add_window(window.window)
			window.window.show()

class ThemeManagerWindow():
	
	def __init__(self, application):
		
		self.application = application
		self.settings = Gio.Settings(schema_id="org.x.theme-manager")
		self.manager = TMBackend()
		self.destop_manager = desktop_theme()
		self.icon_theme = Gtk.IconTheme.get_default()
		
		# Set the Glade file
		gladefile = UI_PATH+"theme-manager.ui"
		self.builder = Gtk.Builder()
		self.builder.add_from_file(gladefile)
		self.window = self.builder.get_object("MainWindow")
		self.window.set_title(_("Theme Manager"))
		
		# Create variables to quickly access dynamic widgets
		self.statusbar = self.builder.get_object("status_bar")
		# input values
		self.color_variants = self.builder.get_object("colour_variants")
		self.systemtheme_variants = self.builder.get_object("system_theme_name")
		self.icontheme_variants = self.builder.get_object("Icon_theme_name")
		self.cursortheme_variants = self.builder.get_object("cursor_theme_name")
		self.user_interval_HH = self.builder.get_object("hour")
		self.user_interval_MM = self.builder.get_object("minute")
		self.user_interval_SS = self.builder.get_object("second")
		
		# Buttons
		self.randomize_button = self.builder.get_object("randomize_theme_button")
		self.save_button = self.builder.get_object("save_button")
		
		# Widget signals
		self.randomize_button.connect("clicked", self.on_random_button)
		self.save_button.connect("clicked", self.on_save_button)
		# self.quit_button.connect("clicked", self.on_quit)
		
		# Menubar
		accel_group = Gtk.AccelGroup()
		self.window.add_accel_group(accel_group)
		menu = self.builder.get_object("main_menu")
		# Add "Start Indicator" option in drop-down menu
		item = Gtk.ImageMenuItem()
		item.set_image(Gtk.Image.new_from_icon_name("theme-manager", Gtk.IconSize.MENU))
		item.set_label(_("Start Indicator"))
		item.connect("activate", self.start_indicator)
		key, mod = Gtk.accelerator_parse("<Control>I")
		item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
		menu.append(item)
		# Add "Show Logs" option in drop-down menu
		item = Gtk.ImageMenuItem()
		item.set_image(Gtk.Image.new_from_icon_name("text-x-log", Gtk.IconSize.MENU))
		item.set_label(_("Show Logs"))
		item.connect("activate", TMIndicator.show_logs, self.window)
		key, mod = Gtk.accelerator_parse("<Control>L")
		item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
		menu.append(item)
		# Add "About" option in drop-down menu
		item = Gtk.ImageMenuItem()
		item.set_image(Gtk.Image.new_from_icon_name("help-about-symbolic", Gtk.IconSize.MENU))
		item.set_label(_("About"))
		item.connect("activate", TMIndicator.open_about, self.window)
		key, mod = Gtk.accelerator_parse("F1")
		item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
		menu.append(item)
		# Add "Quit" option in drop-down menu
		item = Gtk.ImageMenuItem(label=_("Quit"))
		image = Gtk.Image.new_from_icon_name("application-exit-symbolic", Gtk.IconSize.MENU)
		item.set_image(image)
		item.connect('activate', self.on_quit)
		key, mod = Gtk.accelerator_parse("<Control>Q")
		item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
		key, mod = Gtk.accelerator_parse("<Control>W")
		item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
		menu.append(item)
		# Show all drop-down menu options
		menu.show_all()
		
		self.load_conf()
		self.state = self.manager.get_state_info()
		self.currenttheme = self.destop_manager.get_desktop_theme(self.state, self.manager.systemthemename, self.manager.colvariants)
		self.current_status()
	
	def load_conf(self):
		
		self.manager.load_config()
		self.color_variants.set_text(str(self.manager.colorvariants))
		self.systemtheme_variants.set_text(str(self.manager.systemthemename))
		self.icontheme_variants.set_text(str(self.manager.iconthemename))
		self.cursortheme_variants.set_text(str(self.manager.cursorthemename))
		self.user_interval_HH.set_value(self.manager.theme_interval_HH)
		self.user_interval_MM.set_value(self.manager.theme_interval_MM)
		self.user_interval_SS.set_value(self.manager.theme_interval_SS)
	
	def on_quit(self, widget):
		self.application.quit()
	
	def on_random_button(self, widget):
		module_logger.info("User requested change using Randomize button.")
		self.state = self.manager.get_state_info()
		self.nexttheme = self.manager.prep_theme_variants(self.state)
		self.destop_manager.set_desktop_theme(self.state, self.nexttheme)
		self.currenttheme = self.destop_manager.get_desktop_theme(self.state, self.manager.systemthemename, self.manager.colvariants)
		self.current_status()
	
	def on_save_button(self, widget):
		"""Saves user configurations to config file.
		
		Saves user-defined configurations to config file.
		If the config file does not exist, it creates a new
		config file (~/.config/theme-manager/config.cfg)
		in user's home directory.
		"""
		Hr = str(self.user_interval_HH.get_value_as_int())
		Min = str(self.user_interval_MM.get_value_as_int())
		Sec = str(self.user_interval_SS.get_value_as_int())
		user_interval = Hr+':'+Min+':'+Sec
		self.manager.config['system-theme'] = {
			'color-variants': self.color_variants.get_text(),
			'system-theme-name': self.systemtheme_variants.get_text(),
			'icon-theme-name': self.icontheme_variants.get_text(),
			'cursor-theme-name': self.cursortheme_variants.get_text(),
			'theme-interval': user_interval
		}
		with open(CONFIG_FILE, 'w') as f:
				self.manager.config.write(f)
		
		self.load_conf()
	
	def current_status(self):
		'''
		Show current theme info in status bar.
		'''
		status = "DE: %s, \tState: %s, \tVariant: %s, \tLast Updated: %s, \tThemes: %s" % (self.state['DE'], self.state['State'], self.currenttheme["Variant"], self.currenttheme["Last Updated"], self.currenttheme["Themes"])
		
		context_id = self.statusbar.get_context_id("status")
		self.statusbar.push(context_id, status)
	
	def start_indicator(self, widget):
		module_logger.info("Initiaing Theme Manager Indicator from main window.")
		_async(TMIndicator())
		

def run_TMwindow():
	application = theme_manager("org.x.theme-manager", Gio.ApplicationFlags.FLAGS_NONE)
	application.run()
