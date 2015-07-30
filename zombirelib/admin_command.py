import sys

class AdminCommand:
	TAB = "    "
	types = {'v': 'vampire', 'z': 'zombie'}

	def __init__(self, conn, dbc, passwd, sched):
		self.dbc = dbc
		self.connection = conn
		self.passwd = passwd
		self.sched = sched

	def quit(self, players, message=None):
		self.sched.stop()
		self.dbc.save(players)
		if message:
			self.connection.disconnect(message)
		else:
			self.connection.disconnect("I am going away to fill up my tanks. I will be back soon.")
		self.dbc.disconnect()
		print("Zombire bot has exited successfully.")
		sys.exit(0)

	def admin_topscores(self, nick):
		scores = self.dbc.get_admin_topscores()
		if scores:
			i = 1
			self.connection.notice(nick, "#{0}Player{0}Type{0}Score{0}Date".format(self.TAB))
			for s in scores:
				self.connection.notice(nick, "{1}{0}{2}{0}{3}{0}{4}{0}{5}".format(
					self.TAB, i, s[0], self.types[s[1]], s[2], s[3]))
				i += 1
		else:
			self.connection.notice(nick, "No topscores yet.")

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
		elif cmd == "topscores":
			self.admin_topscores(event.source.nick)
