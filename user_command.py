import random

from user import User

class UserCommand:
	types = {'v': 'vampire', 'z': 'zombie'}

	def __init__(self, conn, dbc, channel):
		random.seed()
		self.connection = conn
		self.dbc = dbc
		self.channel = channel

	def register(self, nick):
		User.is_identified(self.connection, nick)

	def register2(self, nick):
		if round(random.random()):
			usertype = "v" # vampire
			icolor = "4"
		else:
			usertype = "z" # zombie
			icolor = "3"
		if self.dbc.register_user(nick, usertype, None):
			self.connection.notice(nick, "You have successfully registered as a \x03{}{}\x03!".format(icolor, self.types[usertype]))
		else:
			self.connection.notice(nick, "You are already registered in the game.")

	def status(self, nick):
		res = self.dbc.get_status(nick)
		if not res:
			self.connection.privmsg(self.channel, "{} is not a registered player.".format(nick))
			return
		[usertype, mpower, points] = res
		if usertype == "v":
			colored_type = "4vampire"
		elif usertype == "z":
			colored_type = "3zombie"
		self.connection.privmsg(self.channel, "{} is a \x03{}\x03. Maximum power: {}. Points: {}."
				.format(nick, colored_type, mpower, points))

	def execute(self, event, command):
		command = command.strip()
		first_space = command.find(" ")
		if first_space == -1:
			cmd = command.lower()
			args = []
		else:
			cmd = command[0:first_space].lower()
			args = command[first_space:].lstrip().split(" ")
		if cmd == "register":
			self.register(event.source.nick)
		if cmd == "status" and len(args) == 1:
			self.status(args[0])
