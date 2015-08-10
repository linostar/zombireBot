import sys

class AdminCommand:
	TAB = "    "
	types = {'v': 'vampire', 'z': 'zombie'}

	def __init__(self, conn, dbc, channel, passwd, access, sched, profiles):
		self.dbc = dbc
		self.connection = conn
		self.channel = channel
		self.passwd = passwd
		self.access = access
		self.sched = sched
		self.profiles = profiles

	def quit(self, players, message=None):
		self.sched.stop()
		self.dbc.save(players, self.profiles)
		if message:
			self.connection.disconnect(message)
		else:
			self.connection.disconnect("I am going away to fill up my tanks. I will be back soon.")
		self.dbc.disconnect()
		print("Zombire bot has exited successfully.")
		sys.exit(0)

	def admin_topscores(self, sender):
		scores = self.dbc.get_admin_topscores()
		if scores:
			i = 1
			self.connection.notice(sender, "#{0}Player{0}Type{0}Score{0}Date".format(self.TAB))
			for s in scores:
				self.connection.notice(sender, "{1}{0}{2}{0}{3}{0}{4}{0}{5}".format(
					self.TAB, i, s[0].replace("..", "[").replace(",,", "]"), self.types[s[1]], s[2], s[3]))
				i += 1
		else:
			self.connection.notice(sender, "No topscores yet.")

	def clearscores(self, sender):
		self.dbc.clear_scores()
		self.connection.notice(sender, "Highscores table has been cleared.")

	def kick(self, sender, players, targets, terminate):
		if players:
			target_list = targets.split(" ")
			for nick in target_list:
				nick2 = nick.replace("[", "..").replace("]", ",,")
				if nick:
					if nick2 in players:
						del players[nick2]
						if terminate:
							del self.profiles[nick2]
							self.dbc.delete_profile(nick2)
						if self.access == "xop":
							self.connection.privmsg("chanserv", "vop {} del {}".format(self.channel, nick))
						elif self.access == "levels":
							self.connection.privmsg("chanserv", "access {} del {}".format(self.channel, nick))
						else: # everything else is considered 'flags'
							self.connection.privmsg("chanserv", "flags {} {} -V".format(self.channel, nick))
						self.connection.notice(sender, "\x02{}\x02 has been removed from the game."
							.format(nick))
					else:
						self.connection.notice(sender, "Error: \x02{}\x02 is not registered in the game."
							.format(nick))
			self.connection.privmsg("chanserv", "sync {}".format(self.channel))
			self.dbc.save(players, self.profiles)
		else:
			self.connection.notice(sender, "There are no players currently in the game.")

	def stats(self, sender, players):
		nb_all = len(players)
		nb_v = len([nick for nick in players if players[nick]['type'] == "v"])
		self.connection.notice(sender, ("{} current player(s), of which {} are \x034vampire(s)\x03 " +
			"and {} are \x033zombie(s)\x03.").format(nb_all, nb_v, nb_all - nb_v))

	def execute(self, event, command, players):
		command = command.strip()
		if not command.startswith(self.passwd + " "):
			self.connection.notice(event.source.nick, "Error: Wrong admin password.")
			return
		command = command[len(self.passwd):].lstrip()
		first_space = command.find(" ")
		if first_space == -1:
			cmd = command.lower()
			args = ""
		else:
			cmd = command[0:first_space].lower()
			args = command[first_space:].lstrip()
		if cmd == "quit":
			self.quit(players, args)
		elif (cmd == "topscores" or cmd == "highscores") and not args:
			self.admin_topscores(event.source.nick)
		elif cmd == "kick" and args:
			self.kick(event.source.nick, players, args.strip().lower(), False)
		elif cmd == "terminate" and args:
			self.kick(event.source.nick, players, args.strip().lower(), True)
		elif cmd == "stats" and not args:
			self.stats(event.source.nick, players)
		elif cmd == "clearscores" and not args:
			self.clearscores(event.source.nick)
		else:
			self.connection.notice(e.source.nick, "Error in command syntax.")
