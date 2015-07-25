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
import yaml
import irc.bot
import irc.strings

from . import user

class zombire(irc.bot.SingleServerIRCBot):
	def __init__(self):
		self.read_config("config.yml")
		irc.bot.SingleServerIRCBot.__init__(self, [(self.config['server'], self.config['port'])],
		self.config['nick'], self.config['realname'])

	def read_config(self, filename):
		if not os.path.exists(filename):
			print('Error: config.yml cannot be found.')
			exit(1)
		with open(filename, 'r') as config_fd:
			self.config = yaml.load(config_fd)

	def on_welcome(self, c, e):
		if self.config['nspass']:
			self.connection.privmsg("nickserv", "identify {}".format(self.config['nspass']))
		for chan in self.config['channels']:
			c.join(chan)

	def on_pubmsg(self, c, e):
		self.connection.notice(e.source.nick, str(e.arguments[0]))

def main():
	bot = zombire()
	bot.start()
	print("Zombire bot is running. To stop the bot, press Ctrl+C.\n")

if __name__ == "__main__":
	main()
