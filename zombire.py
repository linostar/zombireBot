#!/usr/bin/env python3

import os
import yaml
import irc.bot
import irc.strings

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

if __name__ == "__main__":
	main()


