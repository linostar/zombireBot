import random
import datetime

from .user import User
from .utils import Utils

class UserCommand:
	types = {'v': 'vampire', 'z': 'zombie'}
	colors = {'v': 4, 'z': 3}
	colored_types = {'v': '4vampire', 'z': '3zombie'}

	def __init__(self, conn, dbc, channel, access, profiles):
		random.seed()
		self.connection = conn
		self.dbc = dbc
		self.channel = channel
		self.access = access
		self.profiles = profiles

	def howtoplay(self, nick):
		self.connection.notice(nick, "See: " + Utils.HOW_TO_PLAY)

	def register(self, nick):
		User.is_identified(self.connection, nick)

	def register2(self, nick, channels, players):
			#Utils.cs_list = 1
			Utils.registering_nick = nick
			if self.access == "xop":
				#self.connection.privmsg("chanserv", "vop {} list".format(self.channel))
				self.connection.privmsg("chanserv", "vop {} add {}".format(self.channel, nick))
				#self.connection.privmsg("chanserv", "vop {} list".format(self.channel))
			elif self.access == "levels":
				#self.connection.privmsg("chanserv", "access {} list".format(self.channel))
				self.connection.privmsg("chanserv", "access {} add {} 3".format(self.channel, nick))
				#self.connection.privmsg("chanserv", "access {} list".format(self.channel))
			else: # everything else is considered 'flags'
				#self.connection.privmsg("chanserv", "flags {}".format(self.channel))
				self.connection.privmsg("chanserv", "flags {} {} +V".format(self.channel, nick))
				#self.connection.privmsg("chanserv", "flags {}".format(self.channel))
			self.connection.privmsg("chanserv", "sync {}".format(self.channel))
			
	def register3(self, nick, channels, players):
		# approve the registration or not
		# if sorted(Utils.reg_list1) == sorted(Utils.reg_list2):
		# 	self.connection.notice(nick, "You are already registered in the game.")
		# else:
		if random.random() > User.ratio_of_types(players):
			utype = "v" # vampire
		else:
			utype = "z" # zombie
		nick2 = nick.replace("[", "..").replace("]", ",,")
		if self.dbc.register_user(nick2, utype, None):
			players[nick2] = {'type': utype, 'hp': 10, 'mp': 5, 'mmp': 5, 'score': 0, 'bonus': 0}
			if not nick2 in self.profiles:
				self.profiles[nick2] = {'auto': 0, 'extras': 0}
			self.connection.notice(nick, "You have successfully registered as a \x03{}\x03!"
				.format(self.colored_types[utype]))
			if len(players) == 1:
				self.connection.privmsg(self.channel, "\x02A new round of the Game has started!\x02")
				Utils.round_starttime = datetime.datetime.now()
		else:
			self.connection.notice(nick, "Error in registration. A probable cause is " +
				"that you are already registered.")
		Utils.registering_nick = ""

	def unregister(self, nick, players):
		nick2 = nick.replace("[", "..").replace("]", ",,")
		if nick2 in players:
			if self.dbc.unregister_user(nick2):
				del players[nick2]
				self.connection.notice(nick, "You have been removed from the game.")
				if self.access == "xop":
					self.connection.privmsg("chanserv", "vop {} del {}".format(self.channel, nick))
				elif self.access == "levels":
					self.connection.privmsg("chanserv", "access {} del {}".format(self.channel, nick))
				else: # everything else is considered 'flags'
					self.connection.privmsg("chanserv", "flags {} {} -V".format(self.channel, nick))
				self.connection.privmsg("chanserv", "sync {}".format(self.channel))
				self.check_end(players)
				return True
		else:
			self.connection.notice(nick, "Error: you are not registered in this game.")

	def status(self, nick, players):
		nick2 = nick.replace("[", "..").replace("]", ",,")
		if not nick2.lower() in players:
			self.connection.privmsg(self.channel, "{} is not a registered player.".format(nick))
			return
		p = players[nick2.lower()]
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

	def topscores(self):
		msg = ""
		scores = self.dbc.get_topscores()
		if scores:
			for i in range(len(scores)):
				msg += "{}- \x03{}{}\x03 \x02({})\x02. ".format(i+1, self.colors[scores[i][1]], 
					scores[i][0].replace("..", "[").replace(",,", "]"), scores[i][2])
			self.connection.privmsg(self.channel, msg)
		else:
			self.connection.privmsg(self.channel, "No topscores yet.")

	def attack(self, source, target, players):
		source2 = source.replace("[", "..").replace("]", ",,")
		target2 = target.replace("[", "..").replace("]", ",,")
		if not source2.lower() in players:
			self.connection.privmsg(self.channel, "{}: you are not registered in this game."
				.format(source))
		elif not target2.lower() in players:
			self.connection.privmsg(self.channel, "{}: {} isn't registered in this game.".format(
				source, target))
		elif players[source2.lower()]['type'] == players[target2.lower()]['type']:
			self.connection.privmsg(self.channel, "{}: You cannot attack a {} like yourself.".format(
				source, self.types[players[source2.lower()]['type']]))
		elif players[source2.lower()]['mp'] > 0:
			[dice1, dice2, res] = User.battle(source2.lower(), target2.lower(), players)
			self.connection.privmsg(self.channel, ("{} rolled the dice and got \x02{}\x02. " +
				"{} rolled the dice and got \x02{}\x02.").format(source, dice1, target, dice2))
			if res > 0: # attack succeeded
				if players[source2.lower()]['type'] == "v":
					self.connection.privmsg(self.channel, "\x02Attack succeeded.\x02 " +
						"\x034{}\x03 sucked \x02{} HP\x02 of blood from \x033{}\x03.".format(source, res, target))
				else:
					self.connection.privmsg(self.channel, "\x02Attack succeeded.\x02 " +
						"\x033{}\x03 ate \x02{} HP\x02 of brains from \x034{}\x03.".format(source, res, target))
				if User.transform(target2.lower(), players):
					newtype = self.colored_types[players[target2.lower()]['type']]
					self.connection.privmsg(self.channel, ("\x02{}\x02 has lost all of his/her HP " +
						"and has been transformed to a \x03{}\x03.").format(target, newtype))
					if self.check_end(players):
						return
			elif res < 0: # attack failed
				if players[source2.lower()]['type'] == "v":
					self.connection.privmsg(self.channel, "\x02Attack failed.\x02 " +
						"\x033{}\x03 ate \x02{} HP\x02 of brains from \x034{}\x03.".format(target, -res, source))
				else:
					self.connection.privmsg(self.channel, "\x02Attack failed.\x02 " +
						"\x034{}\x03 sucked \x02{} HP\x02 of blood from \x033{}\x03.".format(target, -res, source))
				if User.transform(source2.lower(), players):
					newtype = self.colored_types[players[source2.lower()]['type']]
					self.connection.privmsg(self.channel, ("\x02{}\x02 has lost all of his/her HP " +
						"and has been transformed to a \x03{}\x03.").format(source, newtype))
					if self.check_end(players):
						return
			else: # res == 0 (it's a tie)
				self.connection.privmsg(self.channel, "\x02It is a tie.\x02 No one has been hurt.")
			# check if the max MP is eligible to increase/decrease
			got_new_mmp = User.redetermine_mmp(res, source2.lower(), players)
			if got_new_mmp: new_mmp = players[source2.lower()]['mmp']
			if got_new_mmp == 1:
				self.connection.privmsg(self.channel, ("After {} successful attacks in a row, {} received " +
					"a level-up, and his/her maximum MP became \x02{}\x02.").format(User.CUMULATIVE, source, new_mmp))
			elif got_new_mmp == -1:
				self.connection.privmsg(self.channel, ("After {} failed attacks in a row, {} received " +
					"a level-down, and his/her maximum MP became \x02{}\x02.").format(User.CUMULATIVE, source, new_mmp))
		else:
			self.connection.privmsg(self.channel, "{}: You don't have enough MP to attack other players."
				.format(source))

	def heal(self, source, target, players):
		source2 = source.replace("[", "..").replace("]", ",,")
		target2 = target.replace("[", "..").replace("]", ",,")
		if not source2.lower() in players:
			self.connection.privmsg(self.channel, "{}: you are not registered in this game."
				.format(source))
		elif not target2.lower() in players:
			self.connection.privmsg(self.channel, "{}: {} isn't registered in this game.".format(
				source, target))
		elif source2.lower() == target2.lower():
			self.connection.privmsg(self.channel, "{}: You cannot heal yourself.".format(source))
		elif players[source2.lower()]['type'] != players[target2.lower()]['type']:
			self.connection.privmsg(self.channel, "{}: You cannot heal your enemy.".format(
				source))
		elif players[source2.lower()]['mp'] > 0 and players[source2.lower()]['hp'] > 2:
			User.donate(source2.lower(), target2.lower(), players)
			color = 4 if players[source2.lower()]['type'] == "v" else 3
			self.connection.privmsg(self.channel, ("\x03{0}{1}\x03 sacrificed 2 HP to heal an ally. " +
				"\x03{0}{2}\x03 received 1 HP.").format(color, source, target))
		elif players[source2.lower()]['mp'] > 0:
			self.connection.privmsg(self.channel, "{}: You need at least 3 HP to be able to heal others."
				.format(source))
		else:
			self.connection.privmsg(self.channel, "{}: You don't have enough MP to heal other players."
				.format(source))

	def ambush(self, source, ftarget, starget, players):
		source2 = source.replace("[", "..").replace("]", ",,")
		ftarget2 = ftarget.replace("[", "..").replace("]", ",,")
		starget2 = starget.replace("[", "..").replace("]", ",,")
		if not source2.lower() in players:
			self.connection.privmsg(self.channel, "{}: you are not registered in this game."
				.format(source))
		elif not ftarget2.lower() in players:
			self.connection.privmsg(self.channel, "{}: {} isn't registered in this game.".format(
				source, ftarget))
		elif not starget2.lower() in players:
			self.connection.privmsg(self.channel, "{}: {} isn't registered in this game.".format(
				source, starget))
		elif ftarget2.lower() == starget2.lower():
			self.connection.privmsg(self.channel, "{}: You need to specify two different players."
				.format(source))
		elif players[source2.lower()]['type'] == players[ftarget2.lower()]['type'] or \
		players[ftarget2.lower()]['type'] != players[starget2.lower()]['type']:
			self.connection.privmsg(self.channel, "{}: You cannot attack {}s like yourself.".format(
				source, self.types[players[source2.lower()]['type']]))
		elif players[source2.lower()]['mp'] < 2:
			self.connection.privmsg(self.channel, "{}: You need at least 2 MP to be able to ambush others."
				.format(source))
		elif players[source2.lower()]['hp'] < 6:
			self.connection.privmsg(self.channel, "{}: You need at least 6 HP to be able to ambush others."
				.format(source))
		else: # ambush
			res = User.ambush(source2.lower(), ftarget2.lower(), starget2.lower(), players)
			if res > 0:
				self.connection.privmsg(self.channel, ("\x03{3}{0}\x03 successfully ambushed " +
					"\x03{4}{1}\x03 and \x03{4}{2}\x03. \x03{3}{0}\x03 gained \x026 HP\x02 " +
					"while the other two lost \x023 HP\x02 each.").format(source, ftarget, starget,
					self.colors[players[source2.lower()]['type']], 
					self.colors[players[ftarget2.lower()]['type']]))
				if User.transform(ftarget2.lower(), players):
					newtype = self.colored_types[players[ftarget2.lower()]['type']]
					self.connection.privmsg(self.channel, ("\x02{}\x02 has lost all of his/her HP " +
						"and has been transformed to a \x03{}\x03.").format(ftarget, newtype))
					if self.check_end(players):
						return
				if User.transform(starget2.lower(), players):
					newtype = self.colored_types[players[starget2.lower()]['type']]
					self.connection.privmsg(self.channel, ("\x02{}\x02 has lost all of his/her HP " +
						"and has been transformed to a \x03{}\x03.").format(starget, newtype))
					if self.check_end(players):
						return
			elif res < 0:
				self.connection.privmsg(self.channel, ("\x03{3}{0}\x03's ambush miserably failed " +
					"against \x03{4}{1}\x03 and \x03{4}{2}\x03. \x03{3}{0}\x03 lost \x026 HP\x02 " +
					"while the other two gained \x023 HP\x02 each.").format(source, ftarget, starget,
					self.colors[players[source2.lower()]['type']], 
					self.colors[players[ftarget2.lower()]['type']]))
				if User.transform(source2.lower(), players):
					newtype = self.colored_types[players[source2.lower()]['type']]
					self.connection.privmsg(self.channel, ("\x02{}\x02 has lost all of his/her HP " +
						"and has been transformed to a \x03{}\x03.").format(source, newtype))
					if self.check_end(players):
						return
			else:
				self.connection.privmsg(self.channel, "\x02It is a tie.\x02 No one has been hurt.")
			# check if the max MP is eligible to increase/decrease
			got_new_mmp = User.redetermine_mmp(res, source2.lower(), players)
			if got_new_mmp: new_mmp = players[source2.lower()]['mmp']
			if got_new_mmp == 1:
				self.connection.privmsg(self.channel, ("After {} successful attacks in a row, {} received " +
					"a level-up, and his/her maximum MP became \x02{}\x02.").format(User.CUMULATIVE, source, new_mmp))
			elif got_new_mmp == -1:
				self.connection.privmsg(self.channel, ("After {} failed attacks in a row, {} received " +
					"a level-down, and his/her maximum MP became \x02{}\x02.").format(User.CUMULATIVE, source, new_mmp))

	def list_players(self, utype, players):
		zombires = [nick.replace("..", "[").replace(",,", "]") for nick in players if players[nick]['type'] == utype]
		if zombires:
			self.connection.privmsg(self.channel, "The current \x03{}s\x03 are: ".format(
				self.colored_types[utype]))
			for chunk in Utils.cut_to_chunks(", ".join(zombires)):
				self.connection.privmsg(self.channel, "\x02{}\x02".format(chunk))
		else:
			self.connection.privmsg(self.channel, "No \x03{}s\x03 at the moment.".format(
				self.colored_types[utype]))

	def check_end(self, players):
		winner2 = User.check_if_round_ended(players)
		if winner2 and len(players) > 0:
			diff_time = datetime.datetime.now() - Utils.round_starttime
			winner = winner2.replace("..", "[").replace(",,", "]")
			self.dbc.add_highscore(winner, players[winner2]['type'], players[winner2]['score'])
			self.connection.privmsg(self.channel, "\x02Game set.\x02 The \x03{}s\x03 have won!"
				.format(self.colored_types[players[winner2]['type']]))
			self.connection.privmsg(self.channel, ("\x02{}\x02 is the highscorer in this round, " +
				"with a score of \x02{}\x02.").format(winner, players[winner2]['score']))
			self.connection.privmsg(self.channel, ("This round has lasted for {} day(s), {} " +
				"hour(s), {} minute(s) and {} second(s).").format(diff_time.days, 
				diff_time.seconds//3600, (diff_time.seconds-diff_time.seconds//3600*3600)//60, 
				diff_time.seconds%60))
			User.reset_players(players)
			# in case there are players with auto register on
			self.auto_register(players)
			self.dbc.save(players, self.profiles)
			return True

	def auto_register(self, players):
		list_nicks = []
		for nick in self.profiles:
			if self.profiles[nick]['auto'] & 1: # check bit 0
				if random.random() > User.ratio_of_types(players):
					utype = "v" # vampire
				else:
					utype = "z" # zombie
				players[nick] = {'type': utype, 'hp': 10, 'mp': 5, 'mmp': 5, 'score': 0, 'bonus': 0}
				list_nicks.append(nick.replace("..", "[").replace(",,", "]"))
				if len(players) == 1:
					self.connection.privmsg(self.channel, "\x02A new round of the Game has started!\x02")
					Utils.round_starttime = datetime.datetime.now()
		if len(list_nicks):
			self.connection.privmsg(self.channel, "The following players have been auto-registered:")
			self.connection.privmsg(self.channel, "\x02{}\x02".format(", ".join(list_nicks)))

	def print_version(self):
		self.connection.privmsg(self.channel, "Zombire Bot version: {}".format(Utils.VERSION))

	def get_auto(self, prop, nick):
		res = ""
		prop = prop.lower()
		nick2 = nick.replace("[", "..").replace("]", ",,")
		if prop == "register":
			# bit 0 for on/off
			if self.profiles[nick2]['auto'] & 1:
				res = "on"
			else:
				res = "off"
		elif prop == "heal":
			# bit 2 for highest/lowest, bit 1 for on/off
			if self.profiles[nick2]['auto'] & 2:
				if self.profiles[nick2]['auto'] & 4:
					res = "highest"
				else:
					res = "lowest"
			else:
				res = "off"
		elif prop == "attack":
			# bit 4 for highest/lowest, bit 3 for on/off
			if self.profiles[nick2]['auto'] & 8:
				if self.profiles[nick2]['auto'] & 16:
					res = "highest"
				else:
					res = "lowest"
			else:
				res = "off"
		if res:
			self.connection.notice(nick, "Your auto-{} is \x02{}\x02.".format(prop, res))
		else:
			self.connection.notice(nick, "Incorrect \x02!auto\x02 command syntax.")

	def set_auto(self, prop, val, nick):
		# see bit assignment is get_auto()
		res = True
		prop = prop.lower()
		val = val.lower()
		nick2 = nick.replace("[", "..").replace("]", ",,")
		if prop == "register":
			if val == "on":
				self.profiles[nick2]['auto'] |= 1
			elif val == "off":
				self.profiles[nick2]['auto'] &= ~1
			else:
				res = False
		elif prop == "heal":
			if val == "off":
				self.profiles[nick2]['auto'] &= ~2
			elif val == "lowest":
				self.profiles[nick2]['auto'] &= ~8 # turn auto-attack off
				self.profiles[nick2]['auto'] |= 2
				self.profiles[nick2]['auto'] &= ~4
			elif val == "highest":
				self.profiles[nick2]['auto'] &= ~8 # turn auto-attack off
				self.profiles[nick2]['auto'] |= 2
				self.profiles[nick2]['auto'] |= 4
			else:
				res = False
		elif prop == "attack":
			if val == "off":
				self.profiles[nick2]['auto'] &= ~8
			elif val == "lowest":
				self.profiles[nick2]['auto'] &= ~2 # turn auto-heal off
				self.profiles[nick2]['auto'] |= 8
				self.profiles[nick2]['auto'] &= ~16
			elif val == "highest":
				self.profiles[nick2]['auto'] &= ~2 # turn auto-heal off
				self.profiles[nick2]['auto'] |= 8
				self.profiles[nick2]['auto'] |= 16
			else:
				res = False
		else:
			res = False
		if res:
			self.connection.notice(nick, "Your auto-{} is now set to \x02{}\x02.".format(prop, val))
		else:
			self.connection.notice(nick, "Incorrect \x02!auto\x02 command syntax.")

	def execute(self, event, command, players):
		command = command.strip()
		first_space = command.find(" ")
		if first_space == -1:
			cmd = command.lower()
			args = []
		else:
			cmd = command[0:first_space].lower()
			args = command[first_space:].lstrip().split(" ")
			args = list(filter(lambda x: x.strip(), args))
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
		elif cmd == "ambush" and len(args) == 2:
			self.ambush(event.source.nick, args[0], args[1], players)
		elif cmd == "vampires" and not args:
			self.list_players("v", players)
		elif cmd == "zombies" and not args:
			self.list_players("z", players)
		elif (cmd == "topscores" or cmd == "highscores") and not args:
			self.topscores()
		elif cmd == "howtoplay" and not args:
			self.howtoplay(event.source.nick)
		elif cmd == "version" and not args:
			self.print_version()
		elif cmd == "auto" and len(args) == 1:
			self.get_auto(args[0], event.source.nick.lower())
		elif cmd == "auto" and len(args) == 2:
			self.set_auto(args[0], args[1], event.source.nick.lower())			
