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
			players[nick] = {'type': usertype, 'hp': 10, 'mp': 3, 'mmp': 3, 'score': 0, 'bonus': 0}
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

	def status(self, nick, players):
		if not nick.lower() in players:
			self.connection.privmsg(self.channel, "{} is not a registered player.".format(nick))
			return
		p = players[nick.lower()]
		[utype, hp, mp, mmp, score, bonus] = [p['type'], p['hp'], p['mp'], p['mmp'],
		p['score'], p['bonus']]
		if utype == "v":
			colored_type = "4vampire"
		elif utype == "z":
			colored_type = "3zombie"
		self.connection.privmsg(self.channel, "{} is a \x03{}\x03. HP: {}. MP: {}/{}. Score: {}."
				.format(nick, colored_type, hp, mp, mmp, score))

	def attack(self, source, target, players):
		if not target.lower() in players:
			self.connection.privmsg(self.channel, "{}: {} isn't registered in this game.".format(
				source, target))
		elif not source.lower() in players:
			self.connection.privmsg(self.channel, "{}: you are not registered in this game."
				.format(source))
		elif players[source.lower()]['type'] == players[target.lower()]['type']:
			self.connection.privmsg(self.channel, "{}: You can't attack a {} like yourself.".format(
				source, self.types[players[source.lower()]['type']]))
		elif players[source.lower()]['mp'] > 0:
			players[source.lower()]['mp'] -= 1
			if players[source.lower()]['type'] == "v":
				self.connection.privmsg(self.channel, "Attack succeeded. " +
					"\x034{}\x03 sucked 2 HP of blood from \x033{}\x03.".format(source, target))
			else:
				self.connection.privmsg(self.channel, "Attack succeeded. " +
					"\x033{}\x03 ate 2 HP of brains from \x034{}\x03.".format(source, target))
		else:
			self.connection.privmsg(self.channel, "{}: You don't have enough MP to attack other players."
				.format(source))

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
			self.status(args[0], players)
		if cmd == "attack" and len(args) == 1:
			self.attack(event.source.nick, args[0], players)
