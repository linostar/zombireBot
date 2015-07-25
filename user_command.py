import random

class UserCommand:
	types = {'v': 'vampire', 'z': 'zombie'}

	def __init__(self, conn, dbc, channel):
		random.seed()
		self.connection = conn
		self.dbc = dbc
		self.channel = channel

	def register(self, nick):
		if round(random.random()):
			usertype = "v" # vampire
		else:
			usertype = "z" # zombie
		if self.dbc.register_user(nick, usertype, None):
			self.connection.notice(nick, "You have successfully registered as a {}!".format(self.types[usertype]))
		else:
			self.connection.notice(nick, "You are already registered in the game.")

	def status(self, nick):
		st = self.dbc.get_status(nick)
		if st == "v":
			self.connection.privmsg(self.channel, "{} is a vampire.".format(nick))
		elif st == "z":
			self.connection.privmsg(self.channel, "{} is a zombie.".format(nick))
		else:
			self.connection.privmsg(self.channel, "{} is not a registered player.".format(nick))

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
