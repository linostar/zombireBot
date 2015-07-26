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

	def register2(self, nick, players):
		if round(random.random()):
			usertype = "v" # vampire
			icolor = "4"
		else:
			usertype = "z" # zombie
			icolor = "3"
		if self.dbc.register_user(nick, usertype, None):
			players[nick] = {'type': usertype, 'power': 3, 'mpower': 3, 'points': 10, 'bonus': 0}
			self.connection.notice(nick, "You have successfully registered as a \x03{}{}\x03!".format(
				icolor, self.types[usertype]))
		else:
			self.connection.notice(nick, "You are already registered in the game.")

	def unregister(self, nick, players):
		if nick in players:
			if self.dbc.unregister_user(nick):
				del players[nick]
				self.connection.notice(nick, "You have been removed from the game.")
				return True
		else:
			self.connection.notice(nick, "Error: you are not registered in this game.")

	def status(self, nick):
		res = self.dbc.get_status(nick)
		if not res:
			self.connection.privmsg(self.channel, "{} is not a registered player.".format(nick))
			return
		[usertype, mpower, points, bonus] = res
		if usertype == "v":
			colored_type = "4vampire"
		elif usertype == "z":
			colored_type = "3zombie"
		self.connection.privmsg(self.channel, "{} is a \x03{}\x03. Maximum power: {}. Points: {}."
				.format(nick, colored_type, mpower, points))

	def fight(self, source, target, players):
		if not target in players:
			self.connection.privmsg(self.channel, "{}: {} isn't registered in this game.".format(
				source, target))
		elif not source in players:
			self.connection.privmsg(self.channel, "{}: you are not registered in this game.".format(source))
		elif players[source]['type'] == players[target]['type']:
			self.connection.privmsg(self.channel, "{}: You can't fight a {} like yourself.".format(
				source, self.types[players[source]['type']]))
		else:
			self.connection.privmsg(self.channel, "Fighting to be implemented soon!")

	def execute(self, event, command, players={}):
		command = command.strip()
		first_space = command.find(" ")
		if first_space == -1:
			cmd = command.lower()
			args = []
		else:
			cmd = command[0:first_space].lower()
			args = command[first_space:].lstrip().split(" ")
		if cmd == "register":
			self.register(event.source.nick.lower())
		if cmd == "unregister":
			self.unregister(event.source.nick.lower(), players)
		if cmd == "status" and len(args) == 1:
			self.status(args[0])
		if cmd == "fight" and len(args) == 1:
			self.fight(event.source.nick.lower(), args[0], players)
