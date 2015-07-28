import random

from user import User

class UserCommand:
	types = {'v': 'vampire', 'z': 'zombie'}
	colored_types = {'v': '4vampire', 'z': '3zombie'}

	def __init__(self, conn, dbc, channel):
		random.seed()
		self.connection = conn
		self.dbc = dbc
		self.channel = channel

	def register(self, nick):
		User.is_identified(self.connection, nick)

	def register2(self, nick, players):
		if round(random.random()):
			utype = "v" # vampire
		else:
			utype = "z" # zombie
		if self.dbc.register_user(nick, utype, None):
			players[nick] = {'type': utype, 'hp': 10, 'mp': 3, 'mmp': 3, 'score': 0, 'bonus': 0}
			self.connection.notice(nick, "You have successfully registered as a \x03{}\x03!".format(
				self.colored_types[utype]))
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
		self.connection.privmsg(self.channel, "{} is a \x03{}\x03. HP: {}. MP: {}/{}. Score: {}."
				.format(nick, self.colored_types[utype], hp, mp, mmp, score))

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
			[dice1, dice2, res] = User.battle(source, target, players)
			self.connection.privmsg(self.channel, ("{} threw the dice and got \x02{}\x02. " +
				"{} threw the dice and got \x02{}\x02.").format(source, dice1, target, dice2))
			if res > 0:
				if players[source.lower()]['type'] == "v":
					self.connection.privmsg(self.channel, "\x02Attack succeeded.\x02 " +
						"\x034{}\x03 sucked \x02{} HP\x02 of blood from \x033{}\x03.".format(source, res, target))
				else:
					self.connection.privmsg(self.channel, "\x02Attack succeeded.\x02 " +
						"\x033{}\x03 ate \x02{} HP\x02 of brains from \x034{}\x03.".format(source, res, target))
				if User.transform(target, players):
					newtype = self.colored_types[players[target.lower()]['type']]
					self.connection.privmsg(self.channel, ("{} has lost all of his/her HP " +
						"and has been transformed to a \x03{}\x03.").format(target, newtype))
			elif res < 0:
				if players[source.lower()]['type'] == "v":
					self.connection.privmsg(self.channel, "\x02Attack failed.\x02 " +
						"\x033{}\x03 ate \x02{} HP\x02 of brains from \x034{}\x03.".format(target, -res, source))
				else:
					self.connection.privmsg(self.channel, "\x02Attack failed.\x02 " +
						"\x034{}\x03 sucked \x02{} HP\x02 of blood from \x033{}\x03.".format(target, -res, source))
				if User.transform(source, players):
					newtype = self.colored_types[players[source.lower()]['type']]
					self.connection.privmsg(self.channel, ("{} has lost all of his/her HP " +
						"and has been transformed to a \x03{}\x03.").format(source, newtype))
			else: # res == 0
				self.connection.privmsg(self.channel, "\x02It is a draw.\x02 No one has been hurt.")
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
