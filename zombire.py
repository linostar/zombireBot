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

import sys
import os
import time
import re

import yaml
import irc.client
import irc.bot
import irc.strings

from zombirelib import user_command, admin_command, schedule
from zombirelib.utils import Utils
from zombirelib.db_access import Database


class CustomConnection(irc.client.ServerConnection):
	def privmsg(self, target, text):
		flood_event = schedule.Schedule.get_event()
		flood_event.wait()
		super().privmsg(target, text)

	def notice(self, target, text):
		flood_event = schedule.Schedule.get_event()
		flood_event.wait()
		super().notice(target, text)


class CustomReactor(irc.client.Reactor):
	def server(self):
		c = CustomConnection(self)
		with self.mutex:
			self.connections.append(c)
		return c


class CustomSimpleIRCClient(irc.client.SimpleIRCClient):
	def __init__(self):
		self.reactor = CustomReactor()
		self.connection = self.reactor.server()
		self.dcc_connections = []
		self.reactor.add_global_handler("all_events", self._dispatcher, -10)
		self.reactor.add_global_handler("dcc_disconnect", self._dcc_disconnect, -10)


class CustomSingleServerIRCBot(irc.bot.SingleServerIRCBot, CustomSimpleIRCClient):
	def __init__(self, server_list, nickname, realname, reconnection_interval=60, **connect_params):
		irc.bot.SingleServerIRCBot.__init__(self, server_list, nickname, realname, reconnection_interval=60)


class Zombire(CustomSingleServerIRCBot):
	def __init__(self, config_file):
		self.read_config(config_file)
		self.dbc = Database(self.config)
		self.players = self.dbc.get_players()
		self.profiles = self.dbc.get_profiles()
		self.arsenals = self.dbc.get_arsenals()
		CustomSingleServerIRCBot.__init__(self, [(self.config['server'], self.config['port'])],
		self.config['nick'], self.config['realname'])
		self.sched = schedule.Schedule(self.connection, self.dbc, self.config['channel'],
			self.players, self.profiles, self.arsenals)
		self.uc = user_command.UserCommand(self.connection, self.dbc, self.config['channel'], 
			self.config['channel_accesstype'], self.profiles, self.arsenals)
		self.ac = admin_command.AdminCommand(self.connection, self.dbc, self.config['channel'], 
			str(self.config['admin_passwd']), self.config['channel_accesstype'], self.sched,
			self.profiles, self.arsenals)
		Utils.bosses = Utils.create_bosses()
		Utils.b_created = True

	def read_config(self, filename):
		if not os.path.exists(filename):
			print('Error: config.yml cannot be found.')
			sys.exit(1)
		with open(filename, 'r') as config_fd:
			self.config = yaml.load(config_fd)

	def on_welcome(self, c, e):
		if self.config['nspass']:
			self.connection.privmsg("nickserv", "identify {}".format(self.config['nspass']))
		c.join(self.config['channel'])

	def on_privnotice(self, c, e):
		# checking for nickserv replies
		if e.source.nick.lower() == "nickserv" and e.arguments[0].lower().startswith("status "):
			largs = e.arguments[0].split(" ")
			if largs[2] == "3": # if user is identified to nickserv 
				self.uc.register2(largs[1].lower(), self.channels, self.players) # proceed with the registration
			else:
				self.connection.privmsg(self.config['channel'], ("\x02{}:\x02 You must register your nick first " +
					"through NickServ, or identify if you have already registered it.").format(largs[1]))
			return
		# retrieving chanserv access list for channel
		elif e.source.nick.lower() == "chanserv":
			if Utils.registering_nick:
				args = e.arguments[0]
				detected = re.match(r"all user modes on", args, re.IGNORECASE)
				if detected:
					self.uc.register3(Utils.registering_nick, self.channels, self.players)
					return
			# if Utils.cs_list == 2:
			# 	detected = re.match(r"channel access list", args, re.IGNORECASE)
			# 	if detected:
			# 		Utils.reg_list2 = []
			# 		return
			# 	detected = re.match(r"\d+\.\s+(\w+)\s+", args, re.IGNORECASE)
			# 	if detected:
			# 		Utils.reg_list2.append(detected.group(1).strip().lower())
			# 		return
			# 	detected = re.match(r"end of access list", args, re.IGNORECASE)
			# 	if detected:
			# 		Utils.cs_list = 0
			# 		return
			# elif Utils.cs_list == 1:
			# 	detected = re.match(r"channel access list", args, re.IGNORECASE)
			# 	if detected:
			# 		Utils.reg_list1 = []
			# 		return
			# 	detected = re.match(r"\d+\.\s+(\w+)\s+", args, re.IGNORECASE)
			# 	if detected:
			# 		Utils.reg_list1.append(detected.group(1).strip().lower())
			# 		return
			# 	detected = re.match(r"end of access list", args, re.IGNORECASE)
			# 	if detected:
			# 		Utils.cs_list = 2
			# 		self.uc.register3(Utils.registering_nick, self.channels, self.players)
			# 		return

	def on_privmsg(self, c, e):
		re_exprs = (r"admin\s+(.+)",)
		for expr in re_exprs:
			try:
				detected = re.match(expr, e.arguments[0], re.IGNORECASE)
				raise DetectedCommand
			except DetectedCommand:
				if detected:
					self.ac.execute(e, detected.group(1).strip(), self.players)
					return

	def on_pubmsg(self, c, e):
		re_exprs = (r"\!(register)", r"\!(unregister)", r"\!(status(\s+.+)?)",
			r"\!(attack\s+.+)", r"\!(heal\s+.+)", r"\!(vampires|zombies)", r"\!(version)",
			r"\!(topscores)", r"\!(highscores)", r"\!(howtoplay)", r"\!(ambush\s+.+)",
			r"\!(auto\s+(attack|heal|register|search)(\s+.+)?)", r"\!(challenge)",
			r"\!(search|inventory)", r"\!((use|drop)\s+.+)", r"\!(chest\s+.+)",
			r"\!(forge(\s.+)?)", r"\!(upgrade\s+.+)")
		for expr in re_exprs:
			try:
				detected = re.match(expr, e.arguments[0], re.IGNORECASE)
				raise DetectedCommand
			except DetectedCommand:
				if detected:
					detected_command = detected.group(1).strip()
					if detected_command.lower().startswith(("unregister", "attack", "heal", "ambush",
						"challenge", "auto", "search", "inventory", "use", "drop", "chest", "forge",
						"upgrade")):
						# user needs to be registered to use those commands
						for chname, chobj in self.channels.items():
							voiced_users = list(chobj.voiced()) + list(chobj.opers()) + list(chobj.halfops())
						nick = e.source.nick
						nick2 = nick.replace("[", "..").replace("]", ",,")
						voiced_users = map(lambda x: x.replace("[", "..").replace("]", ",,").lower(), 
							voiced_users)
						if nick2.lower() in voiced_users and nick2.lower() in list(self.players):
							self.uc.execute(e, detected_command, self.players)
						elif nick in voiced_users:
							self.connection.notice(nick, "Error: Please change your nick " +
								"to the one you have registered in the game with.")
						else:
							self.connection.notice(nick, "Error: You are not registered, " +
								"or you did not identify to your nick.")
					else:
						self.uc.execute(e, detected_command, self.players)
					return


class DetectedCommand(Exception):
	# dummy custom Exception, used for simplifying parsing commands
	pass


def main():
	print("Zombire bot is running. To stop the bot, press Ctrl+C.")
	bot = Zombire("conf/config.yml")
	bot.start()

if __name__ == "__main__":
	main()
