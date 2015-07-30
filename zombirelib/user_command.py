import random

from .user import User
from .utils import Utils

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
		if random.random() > User.ratio_of_types(players):
			utype = "v" # vampire
		else:
			utype = "z" # zombie
		if self.dbc.register_user(nick, utype, None):
			players[nick] = {'type': utype, 'hp': 10, 'mp': 5, 'mmp': 5, 'score': 0, 'bonus': 0}
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
		if bonus % 10 == 1:
			bonus_text = "Bonus: +30% attack/defense."
		elif bonus % 10 == 2:
			bonus_text = "Bonus: -30% attack/defense."
		else:
			bonus_text = ""
		self.connection.privmsg(self.channel, "{} is a \x03{}\x03. HP: {}. MP: {}/{}. Score: {}. {}"
				.format(nick, self.colored_types[utype], hp, mp, mmp, score, bonus_text))

	def attack(self, source, target, players):
		if not target.lower() in players:
			self.connection.privmsg(self.channel, "{}: {} isn't registered in this game.".format(
				source, target))
		elif not source.lower() in players:
			self.connection.privmsg(self.channel, "{}: you are not registered in this game."
				.format(source))
		elif players[source.lower()]['type'] == players[target.lower()]['type']:
			self.connection.privmsg(self.channel, "{}: You cannot attack a {} like yourself.".format(
				source, self.types[players[source.lower()]['type']]))
		elif players[source.lower()]['mp'] > 0:
			[dice1, dice2, res] = User.battle(source.lower(), target.lower(), players)
			self.connection.privmsg(self.channel, ("{} threw the dice and got \x02{}\x02. " +
				"{} threw the dice and got \x02{}\x02.").format(source, dice1, target, dice2))
			if res > 0: # attack succeeded
				if players[source.lower()]['type'] == "v":
					self.connection.privmsg(self.channel, "\x02Attack succeeded.\x02 " +
						"\x034{}\x03 sucked \x02{} HP\x02 of blood from \x033{}\x03.".format(source, res, target))
				else:
					self.connection.privmsg(self.channel, "\x02Attack succeeded.\x02 " +
						"\x033{}\x03 ate \x02{} HP\x02 of brains from \x034{}\x03.".format(source, res, target))
				if User.transform(target.lower(), players):
					newtype = self.colored_types[players[target.lower()]['type']]
					self.connection.privmsg(self.channel, ("{} has lost all of his/her HP " +
						"and has been transformed to a \x03{}\x03.").format(target, newtype))
					if self.check_end(players):
						return
			elif res < 0: # attack failed
				if players[source.lower()]['type'] == "v":
					self.connection.privmsg(self.channel, "\x02Attack failed.\x02 " +
						"\x033{}\x03 ate \x02{} HP\x02 of brains from \x034{}\x03.".format(target, -res, source))
				else:
					self.connection.privmsg(self.channel, "\x02Attack failed.\x02 " +
						"\x034{}\x03 sucked \x02{} HP\x02 of blood from \x033{}\x03.".format(target, -res, source))
				if User.transform(source.lower(), players):
					newtype = self.colored_types[players[source.lower()]['type']]
					self.connection.privmsg(self.channel, ("{} has lost all of his/her HP " +
						"and has been transformed to a \x03{}\x03.").format(source, newtype))
					if self.check_end(players):
						return
			else: # res == 0 (it's a tie)
				self.connection.privmsg(self.channel, "\x02It is a tie.\x02 No one has been hurt.")
			# check if the max MP is eligible to increase/decrease
			got_new_mmp = User.redetermine_mmp(res, source.lower(), players)
			if got_new_mmp: new_mmp = players[source.lower()]['mmp']
			if got_new_mmp == 1:
				self.connection.privmsg(self.channel, ("After {} cumulative successful attacks, {} received " +
					"a power-up, and his maximum MP became \x02{}\x02.").format(User.CUMULATIVE, source, new_mmp))
			elif got_new_mmp == -1:
				self.connection.privmsg(self.channel, ("After {} cumulative failed attacks, {} received " +
					"a power-down, and his maximum MP became \x02{}\x02.").format(User.CUMULATIVE, source, new_mmp))
		else:
			self.connection.privmsg(self.channel, "{}: You don't have enough MP to attack other players."
				.format(source))

	def heal(self, source, target, players):
		if not target.lower() in players:
			self.connection.privmsg(self.channel, "{}: {} isn't registered in this game.".format(
				source, target))
		elif not source.lower() in players:
			self.connection.privmsg(self.channel, "{}: you are not registered in this game."
				.format(source))
		elif source.lower() == target.lower():
			self.connection.privmsg(self.channel, "{}: You cannot heal yourself.".format(source))
		elif players[source.lower()]['type'] != players[target.lower()]['type']:
			self.connection.privmsg(self.channel, "{}: You cannot heal your enemy.".format(
				source))
		elif players[source.lower()]['mp'] > 0 and players[source.lower()]['hp'] > 2:
			User.donate(source.lower(), target.lower(), players)
			color = 4 if players[source.lower()]['type'] == "v" else 3
			self.connection.privmsg(self.channel, ("\x03{0}{1}\x03 sacrificed 2 HP to heal an ally. " +
				"\x03{0}{2}\x03 received 1 HP.").format(color, source, target))
		elif players[source.lower()]['mp'] > 0:
			self.connection.privmsg(self.channel, "{}: You need at least 3 HP to be able to heal others."
				.format(source))
		else:
			self.connection.privmsg(self.channel, "{}: You don't have enough MP to heal other players."
				.format(source))

	def list_players(self, utype, players):
		zombires = [nick for nick in players if players[nick]['type'] == utype]
		if zombires:
			self.connection.privmsg(self.channel, "The current \x03{}s\x03 are: ".format(
				self.colored_types[utype]))
			for chunk in Utils.cut_to_chunks(", ".join(zombires)):
				self.connection.privmsg(self.channel, "\x02{}\x02".format(chunk))
		else:
			self.connection.privmsg(self.channel, "No \x03{}s\x03 at the moment.".format(
				self.colored_types[utype]))

	def check_end(self, players):
		winner = User.check_if_round_ended(players)
		if winner:
			self.dbc.add_highscore(winner, players[winner]['type'], players[winner]['score'])
			self.connection.privmsg(self.channel, "\x02Game set.\x02 The \x03{}s\x03 have won!"
				.format(self.colored_types[players[winner]['type']]))
			self.connection.privmsg(self.channel, ("\x02{}\x02 is the highscorer in this round, " +
				"with a score of \x02{}\x02.").format(winner, players[winner]['score']))
			User.reset_players(players)
			self.dbc.save(players)
			return True

	def execute(self, event, command, players):
		command = command.strip()
		first_space = command.find(" ")
		if first_space == -1:
			cmd = command.lower()
			args = []
		else:
			cmd = command[0:first_space].lower()
			args = command[first_space:].lstrip().split(" ")
		if cmd == "register" and not args:
			self.register(event.source.nick.lower())
		elif cmd == "unregister" and not args:
			self.unregister(event.source.nick.lower(), players)
		elif cmd == "status" and len(args) == 1:
			self.status(args[0], players)
		elif cmd == "attack" and len(args) == 1:
			self.attack(event.source.nick, args[0], players)
		elif cmd == "heal" and len(args) == 1:
			self.heal(event.source.nick, args[0], players)
		elif cmd == "vampires" and not args:
			self.list_players("v", players)
		elif cmd == "zombies" and not args:
			self.list_players("z", players)
