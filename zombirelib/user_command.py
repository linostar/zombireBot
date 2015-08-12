import random
import datetime

from .user import User
from .utils import Utils
from .schedule import Schedule

class UserCommand:
	types = {'v': 'vampire', 'z': 'zombie'}
	colors = {'v': 4, 'z': 3}
	colored_types = {'v': '4vampire', 'z': '3zombie'}
	leaders = {'v': 'Count Dracula', 'z': 'General Zombilo'}

	def __init__(self, conn, dbc, channel, access, profiles, arsenals):
		random.seed()
		self.connection = conn
		self.dbc = dbc
		self.channel = channel
		self.access = access
		self.profiles = profiles
		self.arsenals = arsenals

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
			if not nick2 in self.arsenals:
				self.arsenals[nick2] = {'sword': 0, 'slife': 0, 'armor': 0, 'alife': 0}
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

	def status(self, players, source, target=None):
		if not target:
			target = source
		target2 = target.replace("[", "..").replace("]", ",,")
		if not target2.lower() in players:
			self.connection.privmsg(self.channel, "\x02{}\x02 is not a registered player.".format(target))
			return
		p = players[target2.lower()]
		[utype, hp, mp, mmp, score] = [p['type'], p['hp'], p['mp'], p['mmp'], p['score']]
		bonus = User.get_bonus(target2.lower(), players)
		if bonus == 1:
			bonus_text = "Bonus: +30% attack/defense."
		elif bonus == 2:
			bonus_text = "Bonus: -30% attack/defense."
		else:
			bonus_text = ""
		if User.has_chest(target2.lower(), self.profiles):
			chest_text = "1 chest."
		else:
			chest_text = ""
		if Utils.bosses:
			if utype == "v" and Utils.bosses[0]['on']:
				bonus_text = "Power substantially increased due to \x02Dracula\x02 presence."
			elif utype == "z" and Utils.bosses[1]['on']:
				bonus_text = "Power substantially increased due to \x02Zombilo\x02 presence."
		a = self.arsenals[target2.lower()]
		self.connection.privmsg(self.channel, ("\x02{}\x02 is a \x03{}\x03. HP: {}. MP: {}/{}. Score: {}. {}" +
			"Equipment: {} sword ({}) and {} armor ({}). {}").format(target, self.colored_types[utype], hp, mp, mmp, score,
			bonus_text, User.sword_names[a['sword']], a['slife'], User.armor_names[a['armor']], a['alife'], chest_text))

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
			self.connection.privmsg(self.channel, "\x02{}:\x02 you are not registered in this game."
				.format(source))
		elif not target2.lower() in players:
			self.connection.privmsg(self.channel, "\x02{}:\x02 {} isn't registered in this game.".format(
				source, target))
		elif players[source2.lower()]['type'] == players[target2.lower()]['type']:
			self.connection.privmsg(self.channel, "\x02{}:\x02 You cannot attack a {} like yourself.".format(
				source, self.types[players[source2.lower()]['type']]))
		elif User.check_gt(players, source2.lower(), 'mp', 0):
			[dice1, dice2, res] = User.battle(source2.lower(), target2.lower(), players)
			self.connection.privmsg(self.channel, ("\x02{}\x02 rolled the dice and got \x02{}\x02. " +
				"\x02{}\x02 rolled the dice and got \x02{}\x02.").format(source, dice1, target, dice2))
			if res > 0: # attack succeeded
				if players[source2.lower()]['type'] == "v":
					self.connection.privmsg(self.channel, "\x02Attack succeeded.\x02 " +
						"\x034{}\x03 sucked \x02{} HP\x02 of blood from \x033{}\x03.".format(source, res, target))
				else:
					self.connection.privmsg(self.channel, "\x02Attack succeeded.\x02 " +
						"\x033{}\x03 ate \x02{} HP\x02 of brains from \x034{}\x03.".format(source, res, target))
				# add weapon effects
				diff_weapon = User.clash_weapons(res, source2.lower(), target2.lower(), players, self.arsenals)
				if diff_weapon > 0:
					self.connection.privmsg(self.channel, "\x02{}\x02's sword increased the damage by \x02{}\x02."
						.format(source, diff_weapon))
				elif diff_weapon < 0:
					self.connection.privmsg(self.channel, "\x02{}\x02's armor reduced the damage by \x02{}\x02."
						.format(target, -diff_weapon))
				# check for weapon degradation
				if User.degrade_sword(source2.lower(), self.arsenals):
					self.connection.privmsg(self.channel, "\x02{}\x02's sword was destroyed.".format(source))
				if User.degrade_armor(target2.lower(), self.arsenals):
					self.connection.privmsg(self.channel, "\x02{}\x02's armor was destroyed.".format(target))
				# check for player transformation
				if User.transform(target2.lower(), players, source2.lower()):
					newtype = self.colored_types[players[target2.lower()]['type']]
					self.connection.privmsg(self.channel, ("\x02{}\x02 has lost all of his/her HP " +
						"and has been transformed into a \x03{}\x03.").format(target, newtype))
					if self.check_end(players):
						return
			elif res < 0: # attack failed
				if players[source2.lower()]['type'] == "v":
					self.connection.privmsg(self.channel, "\x02Attack failed.\x02 " +
						"\x033{}\x03 ate \x02{} HP\x02 of brains from \x034{}\x03.".format(target, -res, source))
				else:
					self.connection.privmsg(self.channel, "\x02Attack failed.\x02 " +
						"\x034{}\x03 sucked \x02{} HP\x02 of blood from \x033{}\x03.".format(target, -res, source))
				# add weapon effects
				diff_weapon = User.clash_weapons(res, source2.lower(), target2.lower(), players, self.arsenals)
				if diff_weapon > 0:
					self.connection.privmsg(self.channel, "\x02{}\x02's sword increased the damage by \x02{}\x02."
						.format(target, diff_weapon))
				elif diff_weapon < 0:
					self.connection.privmsg(self.channel, "\x02{}\x02's armor reduced the damage by \x02{}\x02."
						.format(source, -diff_weapon))
				# check for weapon degradation
				if User.degrade_armor(source2.lower(), self.arsenals):
					self.connection.privmsg(self.channel, "\x02{}\x02's armor was destroyed.".format(source))
				if User.degrade_sword(target2.lower(), self.arsenals):
					self.connection.privmsg(self.channel, "\x02{}\x02's sword was destroyed.".format(target))
				# check for player transformation
				if User.transform(source2.lower(), players):
					newtype = self.colored_types[players[source2.lower()]['type']]
					self.connection.privmsg(self.channel, ("\x02{}\x02 has lost all of his/her HP " +
						"and has been transformed into a \x03{}\x03.").format(source, newtype))
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
			# will a chest appear?
			if User.chest_appearing(source2.lower(), self.profiles):
				self.connection.privmsg(self.channel, "\x02{}\x02 found a closed chest!".format(source))
		else:
			self.connection.privmsg(self.channel, "\x02{}:\x02 You don't have enough MP to attack other players."
				.format(source))

	def heal(self, source, target, players):
		source2 = source.replace("[", "..").replace("]", ",,")
		target2 = target.replace("[", "..").replace("]", ",,")
		if not source2.lower() in players:
			self.connection.privmsg(self.channel, "\x02{}:\x02 you are not registered in this game."
				.format(source))
		elif not target2.lower() in players:
			self.connection.privmsg(self.channel, "\x02{}:\x02 {} isn't registered in this game.".format(
				source, target))
		elif source2.lower() == target2.lower():
			self.connection.privmsg(self.channel, "\x02{}:\x02 You cannot heal yourself.".format(source))
		elif players[source2.lower()]['type'] != players[target2.lower()]['type']:
			self.connection.privmsg(self.channel, "\x02{}:\x02 You cannot heal your enemy.".format(
				source))
		elif User.check_gt(players, source2.lower(), 'mp', 0) and User.check_gt(players, source2.lower(), 'hp', 2):
			User.donate(source2.lower(), target2.lower(), players)
			color = 4 if players[source2.lower()]['type'] == "v" else 3
			self.connection.privmsg(self.channel, ("\x03{0}{1}\x03 sacrificed 2 HP to heal an ally. " +
				"\x03{0}{2}\x03 received 1 HP.").format(color, source, target))
			# will a chest appear?
			if User.chest_appearing(source2.lower(), self.profiles):
				self.connection.privmsg(self.channel, "\x02{}\x02 found a closed chest!".format(source))
		elif User.check_gt(players, source2.lower(), 'mp', 0):
			self.connection.privmsg(self.channel, "\x02{}:\x02 You need at least 3 HP to be able to heal others."
				.format(source))
		else:
			self.connection.privmsg(self.channel, "\x02{}:\x02 You don't have enough MP to heal other players."
				.format(source))

	def ambush(self, source, ftarget, starget, players):
		source2 = source.replace("[", "..").replace("]", ",,")
		ftarget2 = ftarget.replace("[", "..").replace("]", ",,")
		starget2 = starget.replace("[", "..").replace("]", ",,")
		if not source2.lower() in players:
			self.connection.privmsg(self.channel, "\x02{}:\x02 you are not registered in this game."
				.format(source))
		elif not ftarget2.lower() in players:
			self.connection.privmsg(self.channel, "\x02{}:\x02 {} isn't registered in this game.".format(
				source, ftarget))
		elif not starget2.lower() in players:
			self.connection.privmsg(self.channel, "\x02{}:\x02 {} isn't registered in this game.".format(
				source, starget))
		elif ftarget2.lower() == starget2.lower():
			self.connection.privmsg(self.channel, "\x02{}:\x02 You need to specify two different players."
				.format(source))
		elif players[source2.lower()]['type'] == players[ftarget2.lower()]['type'] or \
		players[ftarget2.lower()]['type'] != players[starget2.lower()]['type']:
			self.connection.privmsg(self.channel, "\x02{}:\x02 You cannot attack {}s like yourself.".format(
				source, self.types[players[source2.lower()]['type']]))
		elif User.check_lt(players, source2.lower(), 'mp', 2):
			self.connection.privmsg(self.channel, "\x02{}:\x02 You need at least 2 MP to be able to ambush others."
				.format(source))
		elif User.check_lt(players, source2.lower(), 'hp', 6):
			self.connection.privmsg(self.channel, "\x02{}:\x02 You need at least 6 HP to be able to ambush others."
				.format(source))
		else: # ambush
			res = User.ambush(source2.lower(), ftarget2.lower(), starget2.lower(), players)
			if res > 0:
				self.connection.privmsg(self.channel, ("\x03{3}{0}\x03 successfully ambushed " +
					"\x03{4}{1}\x03 and \x03{4}{2}\x03. \x03{3}{0}\x03 gained \x026 HP\x02 " +
					"while the other two lost \x023 HP\x02 each.").format(source, ftarget, starget,
					self.colors[players[source2.lower()]['type']], 
					self.colors[players[ftarget2.lower()]['type']]))
				# add weapon effects
				diff_weapon = User.clash_weapons(3, source2.lower(), ftarget2.lower(), players, self.arsenals)
				if diff_weapon > 0:
					self.connection.privmsg(self.channel, "\x02{}\x02's sword increased the damage on \x02{}\x02 by \x02{}\x02."
						.format(source, ftarget, diff_weapon))
				elif diff_weapon < 0:
					self.connection.privmsg(self.channel, "\x02{}\x02's armor reduced the damage by \x02{}\x02."
						.format(ftarget, -diff_weapon))
				diff_weapon = User.clash_weapons(3, source2.lower(), starget2.lower(), players, self.arsenals)
				if diff_weapon > 0:
					self.connection.privmsg(self.channel, "\x02{}\x02's sword increased the damage on \x02{}\x02 by \x02{}\x02."
						.format(source, starget, diff_weapon))
				elif diff_weapon < 0:
					self.connection.privmsg(self.channel, "\x02{}\x02's armor reduced the damage by \x02{}\x02."
						.format(starget, -diff_weapon))
				# check for weapon degradation
				if User.degrade_sword(source2.lower(), self.arsenals):
					self.connection.privmsg(self.channel, "\x02{}\x02's sword was destroyed.".format(source))
				if User.degrade_armor(ftarget2.lower(), self.arsenals):
					self.connection.privmsg(self.channel, "\x02{}\x02's armor was destroyed.".format(ftarget))
				if User.degrade_armor(starget2.lower(), self.arsenals):
					self.connection.privmsg(self.channel, "\x02{}\x02's armor was destroyed.".format(starget))
				# check for player transformation
				if User.transform(ftarget2.lower(), players, source2.lower()):
					newtype = self.colored_types[players[ftarget2.lower()]['type']]
					self.connection.privmsg(self.channel, ("\x02{}\x02 has lost all of his/her HP " +
						"and has been transformed into a \x03{}\x03.").format(ftarget, newtype))
					if self.check_end(players):
						return
				if User.transform(starget2.lower(), players, source2.lower()):
					newtype = self.colored_types[players[starget2.lower()]['type']]
					self.connection.privmsg(self.channel, ("\x02{}\x02 has lost all of his/her HP " +
						"and has been transformed into a \x03{}\x03.").format(starget, newtype))
					if self.check_end(players):
						return
			elif res < 0:
				self.connection.privmsg(self.channel, ("\x03{3}{0}\x03's ambush miserably failed " +
					"against \x03{4}{1}\x03 and \x03{4}{2}\x03. \x03{3}{0}\x03 lost \x026 HP\x02 " +
					"while the other two gained \x023 HP\x02 each.").format(source, ftarget, starget,
					self.colors[players[source2.lower()]['type']], 
					self.colors[players[ftarget2.lower()]['type']]))
				# add weapon effects
				diff_weapon = User.clash_weapons(-3, source2.lower(), ftarget2.lower(), players, self.arsenals)
				if diff_weapon > 0:
					self.connection.privmsg(self.channel, "\x02{}\x02's sword increased the damage on \x02{}\x02 by \x02{}\x02."
						.format(ftarget, source, diff_weapon))
				elif diff_weapon < 0:
					self.connection.privmsg(self.channel, "\x02{}\x02's armor reduced the damage by \x02{}\x02."
						.format(source, -diff_weapon))
				diff_weapon = User.clash_weapons(-3, source2.lower(), starget2.lower(), players, self.arsenals)
				if diff_weapon > 0:
					self.connection.privmsg(self.channel, "\x02{}\x02's sword increased the damage on \x02{}\x02 by \x02{}\x02."
						.format(starget, source, diff_weapon))
				elif diff_weapon < 0:
					self.connection.privmsg(self.channel, "\x02{}\x02's armor reduced the damage by \x02{}\x02."
						.format(source, -diff_weapon))
				# check for weapon degradation
				if User.degrade_armor(source2.lower(), self.arsenals):
					self.connection.privmsg(self.channel, "\x02{}\x02's armor was destroyed.".format(source))
				if User.degrade_sword(ftarget2.lower(), self.arsenals):
					self.connection.privmsg(self.channel, "\x02{}\x02's sword was destroyed.".format(ftarget))
				if User.degrade_sword(starget2.lower(), self.arsenals):
					self.connection.privmsg(self.channel, "\x02{}\x02's sword was destroyed.".format(starget))
				# check for player transformation
				if User.transform(source2.lower(), players):
					newtype = self.colored_types[players[source2.lower()]['type']]
					self.connection.privmsg(self.channel, ("\x02{}\x02 has lost all of his/her HP " +
						"and has been transformed into a \x03{}\x03.").format(source, newtype))
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
			# will a chest appear?
			if User.chest_appearing(source2.lower(), self.profiles):
				self.connection.privmsg(self.channel, "\x02{}\x02 found a closed chest!".format(source))

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
			Schedule.is_bonus_on = False
			User.reset_players(players)
			# in case there are players with auto register on
			self.auto_register(players)
			#self.dbc.save(players, self.profiles)
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
		elif prop == "search":
			# bit 5 for on/off
			if self.profiles[nick2]['auto'] & 32:
				res = "on"
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
				self.profiles[nick2]['auto'] &= ~32 # turn auto-search off
				self.profiles[nick2]['auto'] |= 2
				self.profiles[nick2]['auto'] &= ~4
			elif val == "highest":
				self.profiles[nick2]['auto'] &= ~8 # turn auto-attack off
				self.profiles[nick2]['auto'] &= ~32 # turn auto-search off
				self.profiles[nick2]['auto'] |= 2
				self.profiles[nick2]['auto'] |= 4
			else:
				res = False
		elif prop == "attack":
			if val == "off":
				self.profiles[nick2]['auto'] &= ~8
			elif val == "lowest":
				self.profiles[nick2]['auto'] &= ~2 # turn auto-heal off
				self.profiles[nick2]['auto'] &= ~32 # turn auto-search off
				self.profiles[nick2]['auto'] |= 8
				self.profiles[nick2]['auto'] &= ~16
			elif val == "highest":
				self.profiles[nick2]['auto'] &= ~2 # turn auto-heal off
				self.profiles[nick2]['auto'] &= ~32 # turn auto-search off
				self.profiles[nick2]['auto'] |= 8
				self.profiles[nick2]['auto'] |= 16
			else:
				res = False
		elif prop == "search":
			if val == "on":
				self.profiles[nick2]['auto'] &= ~2 # turn auto-heal off
				self.profiles[nick2]['auto'] &= ~8 # turn auto-attack off
				self.profiles[nick2]['auto'] |= 32
			elif val == "off":
				self.profiles[nick2]['auto'] &= ~32
			else:
				res = False
		else:
			res = False
		if res:
			self.connection.notice(nick, "Your auto-{} is now set to \x02{}\x02.".format(prop, val))
		else:
			self.connection.notice(nick, "Incorrect \x02!auto\x02 command syntax.")

	def challenge(self, source, players):
		source1 = source.replace("..", "[").replace(",,", "]")
		p = players[source.lower()]
		if (p['type'] == "v" and not Utils.bosses[1]['on']) or (p['type'] == "z" and not Utils.bosses[0]['on']):
			self.connection.privmsg(self.channel, "\x02{}:\x02 Your enemy's leader is not around.".format(source1))
		else:
			if User.check_gt(players, source.lower(), 'mp', 0):
				[res, dice1, dice2] = User.challenge_boss(source.lower(), players)
				utype = p['type']
				otype = "v" if utype == "z" else "z"
				self.connection.privmsg(self.channel, ("\x03{}{}\x03 rolled the dice and got \x02{}\x02. " +
					"\x03{}{}\x03 rolled the dice and got \x02{}\x02.").format(self.colors[utype],
					source1, dice1, self.colors[otype], self.leaders[otype], dice2))
				if res > 0:
					if utype == "v":
						self.connection.privmsg(self.channel, ("Whoa! Attack succeeded! \x03{}{}\x03 " +
							"sucked \x02{} HP\x02 of blood from \x03{}{}\x03.").format(self.colors[utype],
							source1, res, self.colors[otype], self.leaders[otype]))
					else:
						self.connection.privmsg(self.channel, ("Whoa! Attack succeeded! \x03{}{}\x03 " +
							"ate \x02{} HP\x02 of brains from \x03{}{}\x03.").format(self.colors[utype],
							source1, res, self.colors[otype], self.leaders[otype]))
				elif res < 0:
					if utype == "v":
						self.connection.privmsg(self.channel, ("Muwhahaha! Attack failed! \x03{}{}\x03 " +
							"ate \x02{} HP\x02 of brains from \x03{}{}\x03.").format(self.colors[otype],
							self.leaders[otype], -res, self.colors[utype], source1))
					else:
						self.connection.privmsg(self.channel, ("Muwhahaha! Attack failed! \x03{}{}\x03 " +
							"sucked \x02{} HP\x02 of blood from \x03{}{}\x03.").format(self.colors[otype],
							self.leaders[otype], -res, self.colors[utype], source1))
					if User.transform(source.lower(), players):
						newtype = self.colored_types[players[source.lower()]['type']]
						self.connection.privmsg(self.channel, ("\x02{}\x02 has lost all of his/her HP " +
							"and has been transformed into a \x03{}\x03.").format(source1, newtype))
						if self.check_end(players):
							return
				else:
					self.connection.privmsg(self.channel, "\x02It is a tie.\x02 No one has been hurt.")
				# check if the max MP is eligible to increase/decrease
				got_new_mmp = User.redetermine_mmp(res, source.lower(), players)
				if got_new_mmp: new_mmp = players[source.lower()]['mmp']
				if got_new_mmp == 1:
					self.connection.privmsg(self.channel, ("After {} successful attacks in a row, {} received " +
						"a level-up, and his/her maximum MP became \x02{}\x02.").format(User.CUMULATIVE, source1, new_mmp))
				elif got_new_mmp == -1:
					self.connection.privmsg(self.channel, ("After {} failed attacks in a row, {} received " +
						"a level-down, and his/her maximum MP became \x02{}\x02.").format(User.CUMULATIVE, source1, new_mmp))
			else:
				self.connection.profiles(self.channel, "\x02{}:\x02 You do not have enough MP.".format(source1))

	def search(self, source, players):
		source2 = source.replace("[", "..").replace("]", ",,")
		if source2.lower() in self.profiles and source2.lower() in players:
			if User.check_gt(players, source2.lower(), 'mp', 0):
				item = User.add_item(source2.lower(), self.profiles, players)
				if item == -1:
					self.connection.notice(source, "You cannot search for items. Your inventory is already full.")
					return
				if item:
					self.connection.notice(source, "Lucky! You found \x02{}\x02."
						.format(User.item_names[item]))
				else:
					self.connection.notice(source, "You did not find any item this time.")
			else:
				self.connection.notice(source, "You do not have enough MP to search for items.")

	def inventory(self, source):
		source2 = source.replace("[", "..").replace("]", ",,")
		if source2.lower() in self.profiles:
			msg = ""
			items = User.get_inventory(source2.lower(), self.profiles)
			for i in range(3):
				if items[i]:
					msg += "\x02{}- {}.\x02 ".format(i+1, User.item_names[items[i]])
			if msg:
				self.connection.notice(source, "Your inventory contains: " + msg)
			else:
				self.connection.notice(source, "Your inventory is empty.")

	def use(self, source, players, item_index, target=None):
		source2 = source.replace("[", "..").replace("]", ",,")
		type1 = players[source2.lower()]['type']
		try:
			if item_index not in ("1", "2", "3"):
				item_index = "x" # goto except line
			item_index = int(item_index)
			if source2.lower() in self.profiles:
				item = User.get_item(item_index-1, source2.lower(), self.profiles)
				if item:
					if item in (8, 9, 10, 11, 12, 13): # needs a target
						if not target:
							self.connection.notice(source, "You need to specify a target for this item use.")
							return
						target2 = target.replace("[", "..").replace("]", ",,")
						if target2.lower() in players:
							type2 = players[target2.lower()]['type']
							# check restrictions on some items before using them
							if item not in (10, 11):
								User.use_item2(item, source2.lower(), target2.lower(), players)
							msg = "\x03{0}{1}\x03 used \x02{2}\x02 on \x03{3}{4}\x03. "
							if item == 8:
								msg += "The explosion lowered the HP of both to \x021\x02."
							elif item == 9:
								msg += "As a result, \x03{3}{4}\x03 lost all his/her bonus effects."
							elif item == 10:
								if players[source2.lower()]['mp'] == players[source2.lower()]['mmp']:
									User.use_item2(item, source2.lower(), target2.lower(), players)
									msg += "As a result, each of the two has now the other player's HP stats."
								else:
									self.connection.notice(source, "You need to have full MP to use this item.")
									return
							elif item == 11:
								if User.check_lt(players, source2.lower(), 'mp', 1):
									self.connection.notice(source, "You do not have any MP to use this item.")
									return
								User.use_item2(item, source2.lower(), target2.lower(), players)
								msg += "He/she sacrificed 1 MP to decrease \x03{3}{4}\x03's HP by 5."
							elif item == 12:
								msg2 = ""
								User.drop_item(item_index-1, source2.lower(), self.profiles)
								items = User.get_inventory(target2.lower(), self.profiles)
								self.connection.privmsg(self.channel, msg.format(
									self.colors[type1], source, User.item_names[item], self.colors[type2], target))
								for i in range(3):
									if items[i]:
										msg2 += "\x02{}- {}.\x02 ".format(i+1, User.item_names[items[i]])
								if msg2:
									self.connection.notice(source, "\x02{}\x02's inventory contains: {}".format(target, msg2))
								else:
									self.connection.notice(source, "\x02{}\x02's inventory is empty.".format(target))
							elif item == 13:
								items = User.get_inventory(target2.lower(), self.profiles)
								nz_items = [x for x in items if x]
								if len(nz_items):
									choice = random.randrange(0, len(nz_items))
									User.drop_item(item_index-1, source2.lower(), self.profiles)
									stolen_item = items[choice]
									res = User.append_item(stolen_item, source2.lower(), self.profiles)
									self.connection.privmsg(self.channel, msg.format(
										self.colors[type1], source, User.item_names[item], self.colors[type2], target))
									User.drop_item(choice, target2.lower(), self.profiles)
									if res:
										self.connection.privmsg(self.channel, "\x02{}\x02 stole \x02{}\x02 from \x02{}\x02."
											.format(source, User.item_names[stolen_item], target))
									else:
										self.connection.privmsg(self.channel, ("\x02{}\x02 tried to steal \x02{}\x02 from \x02{}\x02 " +
											"but had to drop it because he/she already had one of those.").format(source,
											User.item_names[stolen_item], target))
								else:
									User.drop_item(item_index-1, source2.lower(), self.profiles)
									self.connection.privmsg(self.channel, msg.format(
										self.colors[type1], source, User.item_names[item], self.colors[type2], target))
									self.connection.privmsg(self.channel, ("\x02{}\x02 couldn't steal anything because " +
										"\x02{}\x02's inventory was empty.").format(source, target))
							# remove item after it was consumed
							if item not in (12, 13):
								User.drop_item(item_index-1, source2.lower(), self.profiles)
								self.connection.privmsg(self.channel, msg.format(
									self.colors[type1], source, User.item_names[item], self.colors[type2], target))
							if item == 11:
								if User.transform(target2.lower(), players, source2.lower()):
									newtype = self.colored_types[players[target2.lower()]['type']]
									self.connection.privmsg(self.channel, ("\x02{}\x02 has lost all of his/her HP " +
										"and has been transformed into a \x03{}\x03.").format(target, newtype))
						else:
							self.connection.notice(source, "You cannot use the item on someone who is not playing in this round.")
					else: # does not need a target
						if target:
							self.connection.notice(source, "You cannot use this item on other players.")
							return
						if item != 14:
							User.use_item(item, source2.lower(), players)
						msg = "\x03{0}{1}\x03 consumed a \x02{2}\x02. "
						if item == 1:
							msg += "His/her HP increased by \x022\x02."
						elif item == 2:
							msg += "His/her HP increased by \x025\x02."
						elif item == 3:
							msg += "His/her HP increased by \x0210\x02."
						elif item == 4:
							msg += "His/her MP increased by \x021\x02."
						elif item == 5:
							msg += "His/her MP increased by \x022\x02."
						elif item == 6:
							msg += "His/her MP increased by \x023\x02."
						elif item == 7:
							newtype = players[source2.lower()]['type']
							msg += "He/she transformed into a \x03" + self.colored_types[newtype] + "\x03."
						elif item == 14:
							if User.check_gt(players, source2.lower(), 'hp', 20):
								User.use_item(item, source2.lower(), players)
								boss_index = 0 if type1 == "v" else 1
								if User.summon_boss(boss_index):
									User.drop_item(item_index-1, source2.lower(), self.profiles)
									self.connection.privmsg(self.channel, msg.format(
										self.colors[type1], source, User.item_names[item]))
									self.connection.privmsg(self.channel, "\x03{}{}\x03 will arrive in 1 minute."
										.format(self.colors[type1], self.leaders[type1]))
								else:
									self.connection.notice(source, "You cannot use this item now because your leader is already here.")
							else:
								self.connection.notice(source, "You need to have more than 20 HP to use this item.")
						# remove item after it was consumed
						if item != 14:
							User.drop_item(item_index-1, source2.lower(), self.profiles)
							self.connection.privmsg(self.channel, msg.format(
								self.colors[type1], source, User.item_names[item]))
					if item in (7, 11):
						self.check_end(players)
				else:
					self.connection.notice(source, "Item \x02#{}\x02 does not exist in your inventory."
						.format(item_index))
		except ValueError:
			self.connection.notice(source, "You can only enter a number between 1 and 3 after this command.")

	def drop(self, source, item_index):
		source2 = source.replace("[", "..").replace("]", ",,")
		try:
			if item_index not in ("1", "2", "3"):
				item_index = "x" # goto except line
			item_index = int(item_index)
			if source2.lower() in self.profiles:
				item = User.get_item(item_index-1, source2.lower(), self.profiles)
				if item:
					User.drop_item(item_index-1, source2.lower(), self.profiles)
					self.connection.notice(source, "You have dropped item #{}: \x02{}\x02."
						.format(item_index, User.item_names[item]))
				else:
					self.connection.notice(source, "Item \x02#{}\x02 does not exist in your inventory."
						.format(item_index))
		except ValueError:
			self.connection.notice(source, "You can only enter a number between 1 and 3 after this command.")

	def chest(self, action, source):
		source2 = source.replace("[", "..").replace("]", ",,")
		if not action in ("open", "drop"):
			self.connection.notice(source, "Error: unrecognized action on chest.")
			return
		if not User.has_chest(source2.lower(), self.profiles):
			self.connection.notice(source, "You don't have any chest in your possession.")
			return
		if action == "open":
			ore = User.add_to_forge(source2.lower(), self.profiles)
			if ore == -1:
				self.connection.notice(source, "You couldn't open the chest because there is no empty space in your forge.")
				return
			if ore:
				self.connection.notice(source, "You found a \x02{}\x02 in the chest.".format(User.ore_names[ore]))
			else:
				self.connection.notice(source, "The chest was empty.")
		User.drop_chest(source2.lower(), self.profiles)
		if action == "drop":
			self.connection.notice(source, "You dropped the chest.")

	def forge_list(self, source):
		source2 = source.replace("[", "..").replace("]", ",,")
		ores = User.get_forge(source2.lower(), self.profiles)
		if not ores[0]:
			self.connection.notice(source, "Your forge is empty.")
			return
		msg = "Your forge contains: "
		for i in range(3):
			if not ores[i]:
				break
			msg += "\x02{}- {}.\x02".format(i+1, User.ore_names[ores[i]])
		self.connection.notice(source, msg)

	def forge_change(self, source, action, ore_index):
		source2 = source.replace("[", "..").replace("]", ",,")
		if action.lower() == "drop":
			try:
				ore_index = int(ore_index)
				if ore_index not in (1, 2, 3):
					self.connection.notice(source, "You can only enter a number between 1 and 3 after !forge drop.")
					return
				if User.drop_from_forge(ore_index, source2.lower(), self.profiles):
					self.connection.notice(source, "Ore \x02#{}\x02 was dropped from your forge."
						.format(ore_index))
				else:
					self.connection.notice(source, "Ore \x02#{}\x02 does not exist in your forge."
						.format(ore_index))
			except ValueError:
				self.connection.notice(source, "You can only enter a number between 1 and 3 after !forge drop.")
		else:
			self.connection.notice(source, "Incorrect !forge command syntax.")

	def arsenal_upgrade(self, source, weapon):
		source2 = source.replace("[", "..").replace("]", ",,")
		weapon = weapon.lower()
		if weapon == "sword":
			sword = User.upgrade_sword(source2.lower(), self.profiles, self.arsenals)
			if sword:
				self.connection.privmsg(self.channel, "\x02{}\x02 has upgraded his sword to \x02{} sword\x02."
					.format(source, User.sword_names[sword]))
			else:
				self.connection.notice(source, "You don't have the necessary ores to upgrade your sword.")
		elif weapon == "armor":
			armor = User.upgrade_armor(source2.lower(), self.profiles, self.arsenals)
			if armor:
				self.connection.privmsg(self.channel, "\x02{}\x02 has upgraded his armor to \x02{} armor\x02."
					.format(source, User.armor_names[armor]))
			else:
				self.connection.notice(source, "You don't have the necessary ores to upgrade your armor.")
		else:
			self.connection.notice(source, "Incorrect !upgrade command syntax.")

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
		elif cmd == "status" and not args:
			self.status(players, event.source.nick)
		elif cmd == "status" and len(args) == 1:
			self.status(players, event.source.nick, args[0])
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
		elif cmd == "challenge" and not args:
			self.challenge(event.source.nick, players)
		elif cmd == "search" and not args:
			self.search(event.source.nick, players)
		elif cmd == "inventory" and not args:
			self.inventory(event.source.nick)
		elif cmd == "use" and len(args) == 1:
			self.use(event.source.nick, players, args[0])
		elif cmd == "use" and len(args) == 2:
			self.use(event.source.nick, players, args[0], args[1])
		elif cmd == "drop" and len(args) == 1:
			self.drop(event.source.nick, args[0])
		elif cmd == "chest" and len(args) == 1:
			self.chest(args[0].lower(), event.source.nick)
		elif cmd == "forge" and not args:
			self.forge_list(event.source.nick)
		elif cmd == "forge" and len(args) == 2:
			self.forge_change(event.source.nick, args[0], args[1])
		elif cmd == "upgrade" and len(args) == 1:
			self.arsenal_upgrade(event.source.nick, args[0])
