#!/usr/bin/env python3

#    Zombire IRC game bot
#    Copyright (C) 2015  Linostar <linux.anas@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re

import yaml
import irc.bot
import irc.strings

import user_command, admin_command

class Zombire(irc.bot.SingleServerIRCBot):
	def __init__(self):
		self.read_config("config.yml")
		irc.bot.SingleServerIRCBot.__init__(self, [(self.config['server'], self.config['port'])],
		self.config['nick'], self.config['realname'])
		self.uc = user_command.UserCommand()
		self.ac = admin_command.AdminCommand(self.connection)

	def read_config(self, filename):
		if not os.path.exists(filename):
			print('Error: config.yml cannot be found.')
			exit(1)
		with open(filename, 'r') as config_fd:
			self.config = yaml.load(config_fd)

	def on_welcome(self, c, e):
		if self.config['nspass']:
			self.connection.privmsg("nickserv", "identify {}".format(self.config['nspass']))
		c.join(self.config['channel'])

	def on_privmsg(self, c, e):
		c.privmsg(e.target, "Echo: " + str(e.arguments[0]))
		command = re.match(r"admin\s+(.+)", str(e.arguments[0]), re.IGNORECASE).group(1).strip()
		if command:
			self.ac.execute(command)
			return

	def on_pubmsg(self, c, e):
		c.privmsg(e.target, "Echo: " + str(e.arguments[0]))
		command = re.match(r"\!admin\s+(.+)", str(e.arguments[0]), re.IGNORECASE).group(1).strip()

def main():
	print("Zombire bot is running. To stop the bot, press Ctrl+C.")
	bot = Zombire()
	bot.start()

if __name__ == "__main__":
	main()
