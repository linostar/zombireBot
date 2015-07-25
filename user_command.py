import random

class UserCommand:
	types = {'v': 'vampire', 'z': 'zombie'}

	def __init__(self, conn, dbc):
		random.seed()
		self.connection = conn
		self.dbc = dbc

	def register(self, nick):
		if round(random.random()):
			usertype = "v" # vampire
		else:
			usertype = "z" # zombie
		if self.dbc.register_user(nick, usertype, None):
			self.connection.notice(nick, "You have successfully registered as a {}!".format(self.types[usertype]))
		else:
			self.connection.notice(nick, "You are already registered in the game.")

	def execute(self, event, command):
		command = command.strip()
		first_space = command.find(" ")
		if first_space == -1:
			cmd = command.lower()
			args = ""
		else:
			cmd = command[0:first_space].lower()
			args = command[first_space:].lstrip()
		if cmd == "register":
			self.register(event.source.nick)
