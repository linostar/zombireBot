import threading
import datetime
import time
import random
import math
import queue

from .user import User
from .utils import Utils

class Schedule:
	X_LINES = 1
	Y_SECONDS = 1
	equeue = queue.Queue()
	loop = True
	is_bonus_on = False
	last_hour_mp = -1
	last_hour_bonus = -1
	last_hour_auto = -1
	colors = {'v': 4, 'z': 3}
	colored_types = {'v': '4vampire', 'z': '3zombie'}
	bonus_vars = []
	bonus_texts = ("The following players found \x02{}\x02. Upon consuming it, they temporarily gained \x0230%\x02 boost on attack/defense: ", 
		"The following players \x02{}\x02. Due to that, they temporarily lost \x0230%\x02 of their attack/defense: ")
	bonus_vars.append(("a Red Bull", "Mega Steroids", "Elixir", "a Super Vaccine", "Blueberry Pancakes", "Mega Potion",
		"a delicious Honeypot", "a Rainbow Cake"))
	bonus_vars.append(("caught swine flu", "got bitten by a venomous snake", "got stinged by a wasp", "fell in a deep hole",
		"got attacked by a wolf", "suffered from Vitamin C deficiency"))
	msg_boss_join = ["\x034Count Dracula\x03 has arrived to the battlefield. His presence substantially boosted the morale of all vampires.",
	"\x033General Zombilo\x03 has arrived to the battlefield. His presence substantially boosted the morale of all zombies."]
	msg_boss_leave = ["\x034Count Dracula\x03 just left the battlefield.", "\x033General Zombilo\x03 just left the battlefield."]
	msg_boss_name = ["<Count Dracula> ", "<General Zombilo> "]
	msg_boss_taunt = [("BRING ME SOME BLOODY ZOMBIE SOUP!", "WE WILL SUCK THEIR BRAINS DRY!", "BRING IT ON, YOU GREENISH PUKE MONSTERS!"),
	("ZOMBIES, WHAT IS YOUR PROFESSION?", "WE WILL MAKE NECKLACES FROM THEIR FANGS!", "TONIGHT WE DINE ON THOSE BLOODY SUCKERS!")]

	def __init__(self, conn, dbc, channel, players, profiles):
		random.seed()
		self.connection = conn
		self.dbc = dbc
		self.channel = channel
		self.players = players
		self.profiles = profiles
		misc_thread = threading.Thread(target=self.misc_tasks)
		misc_thread.start()
		bonus_thread = threading.Thread(target=self.give_bonus)
		bonus_thread.start()
		flood_thread = threading.Thread(target=self.process_msg)
		flood_thread.start()
		autoaction_thread = threading.Thread(target=self.auto_action)
		autoaction_thread.start()

	@staticmethod
	def get_event():
		e = threading.Event()
		e.clear()
		Schedule.equeue.put(e)
		return e

	def process_msg(self):
		while self.loop:
			if not Schedule.equeue.empty():
				e = Schedule.equeue.get()
				e.set()
			time.sleep(Schedule.Y_SECONDS)

	def auto_action(self):
		while self.loop:
			if len(self.players) > 1:
				now_hour = datetime.datetime.now().hour
				now_min = datetime.datetime.now().minute
				now_sec = datetime.datetime.now().second
				if now_min == 55 and now_sec >= 0 and now_sec < 10 and self.last_hour_auto != now_hour:
					self.last_hour_auto = now_hour
					for nick in self.profiles:
						if nick in self.players:
							if User.check_gt(self.players, nick, 'mp', 0):
								utype = self.players[nick]['type']
								otype = "v" if utype == "z" else "z"
								if self.profiles[nick]['auto'] & 2: # auto-heal
									if User.check_gt(self.players, nick, 'hp', 2):
										pfilter = {x:self.players[x]['hp'] for x in self.players
											if self.players[x]['type'] == utype and x != nick}
										if list(pfilter):
											if self.profiles[nick]['auto'] & 4: # highest
												target = max(pfilter, key=pfilter.get)
											else: #lowest
												target = min(pfilter, key=pfilter.get)
											User.donate(nick, target, self.players)
											nick1 = nick.replace("..", "[").replace(",,", "]")
											target1 = target.replace("..", "[").replace(",,", "]")
											self.connection.privmsg(self.channel, "\x03{0}{1}\x03 auto-healed \x03{0}{2}\x03."
												.format(self.colors[utype], nick1, target1))
								elif self.profiles[nick]['auto'] & 32: # auto-search
									nick1 = nick.replace("..", "[").replace(",,", "]")
									new_item = User.add_item(nick, self.profiles, self.players)
									if new_item == -1:
										self.connection.notice(nick1, "Auto-search: You cannot search for items because your inventory is full.")
									elif new_item:
										self.connection.notice(nick1, "Auto-search: Lucky! You found \x02{}\x02."
											.format(User.item_names[new_item]))
									else:
										self.connection.notice(nick1, "Auto-search: You did not find any item this time.")
								elif self.profiles[nick]['auto'] & 8: # auto-attack
									pfilter = {x:self.players[x]['hp'] for x in self.players
										if self.players[x]['type'] != utype}
									if list(pfilter):
										if self.profiles[nick]['auto'] & 16: # highest
											target = max(pfilter, key=pfilter.get)
										else: #lowest
											target = min(pfilter, key=pfilter.get)
										nick1 = nick.replace("..", "[").replace(",,", "]")
										target1 = target.replace("..", "[").replace(",,", "]")
										[dice1, dice2, diff_dice] = User.battle(nick, target, self.players)
										if diff_dice > 0:
											self.connection.privmsg(self.channel, ("\x03{0}{1}\x03 auto-attacked \x03{2}{3}\x03" +
												" and succeeded, gaining \x02{4} HP\x02 in the process.").format(self.colors[utype],
												nick1, self.colors[otype], target1, diff_dice))
											if User.transform(target, self.players, nick):
												newtype = self.colored_types[utype]
												self.connection.privmsg(self.channel, ("\x02{}\x02 has lost all of his/her HP " +
													"and has been transformed to a \x03{}\x03.").format(target1, newtype))
												if self.check_end():
													break
										elif diff_dice < 0:
											self.connection.privmsg(self.channel, ("\x03{0}{1}\x03 auto-attacked \x03{2}{3}\x03" +
												" and failed, losing \x02{4} HP\x02 in the process.").format(self.colors[utype],
												nick1, self.colors[otype], target1, -diff_dice))
											if User.transform(nick, self.players):
												newtype = self.colored_types[otype]
												self.connection.privmsg(self.channel, ("\x02{}\x02 has lost all of his/her HP " +
													"and has been transformed to a \x03{}\x03.").format(nick1, newtype))
												if self.check_end():
													break
										else:
											self.connection.privmsg(self.channel, ("\x03{0}{1}\x03 tried to auto-attack \x03{2}{3}\x03" +
												" but it was a tie and no one was hurt.").format(self.colors[utype],
												nick1, self.colors[otype], target1))
										# check if the max MP is eligible to increase/decrease
										got_new_mmp = User.redetermine_mmp(diff_dice, nick, self.players)
										if got_new_mmp: new_mmp = self.players[nick]['mmp']
										if got_new_mmp == 1:
											self.connection.privmsg(self.channel, ("After {} successful attacks in a row, {} received " +
												"a level-up, and his/her maximum MP became \x02{}\x02.").format(User.CUMULATIVE, nick1, new_mmp))
										elif got_new_mmp == -1:
											self.connection.privmsg(self.channel, ("After {} failed attacks in a row, {} received " +
												"a level-down, and his/her maximum MP became \x02{}\x02.").format(User.CUMULATIVE, nick1, new_mmp))
			time.sleep(5)

	def check_end(self):
		winner2 = User.check_if_round_ended(self.players)
		if winner2 and len(self.players) > 0:
			diff_time = datetime.datetime.now() - Utils.round_starttime
			winner = winner2.replace("..", "[").replace(",,", "]")
			self.dbc.add_highscore(winner, self.players[winner2]['type'], self.players[winner2]['score'])
			self.connection.privmsg(self.channel, "\x02Game set.\x02 The \x03{}s\x03 have won!"
				.format(self.colored_types[self.players[winner2]['type']]))
			self.connection.privmsg(self.channel, ("\x02{}\x02 is the highscorer in this round, " +
				"with a score of \x02{}\x02.").format(winner, self.players[winner2]['score']))
			self.connection.privmsg(self.channel, ("This round has lasted for {} day(s), {} " +
				"hour(s), {} minute(s) and {} second(s).").format(diff_time.days, 
				diff_time.seconds//3600, (diff_time.seconds-diff_time.seconds//3600*3600)//60, 
				diff_time.seconds%60))
			Schedule.is_bonus_on = False
			User.reset_players(self.players)
			# in case there are players with auto register on
			self.auto_register()
			#self.dbc.save(self.players, self.profiles)
			return True

	def auto_register(self):
		list_nicks = []
		for nick in self.profiles:
			if self.profiles[nick]['auto'] & 1: # check bit 0
				if random.random() > User.ratio_of_types(self.players):
					utype = "v" # vampire
				else:
					utype = "z" # zombie
				self.players[nick] = {'type': utype, 'hp': 10, 'mp': 5, 'mmp': 5, 'score': 0, 'bonus': 0}
				list_nicks.append(nick.replace("..", "[").replace(",,", "]"))
				if len(self.players) == 1:
					self.connection.privmsg(self.channel, "\x02A new round of the Game has started!\x02")
					Utils.round_starttime = datetime.datetime.now()
		if len(list_nicks):
			self.connection.privmsg(self.channel, "The following players have been auto-registered:")
			self.connection.privmsg(self.channel, "\x02{}\x02".format(", ".join(list_nicks)))

	def misc_tasks(self):
		while self.loop:
			if self.players:
				now_hour = datetime.datetime.now().hour
				now_min = datetime.datetime.now().minute
				now_sec = datetime.datetime.now().second
				# create bosses
				if Utils.b_created and Utils.bosses:
					if Utils.bosses[0]['shown'] and Utils.bosses[1]['shown'] and not Utils.bosses[0]['on'] \
					and not Utils.bosses[1]['on']:
						#Utils.bosses[0]['shown'] = False
						#Utils.bosses[1]['shown'] = False
						Utils.b_created = False
				if now_hour == 0 and now_min == 0 and now_sec >=0 and now_sec < 6 and not Utils.b_created:
					Utils.b_created = True
					Utils.bosses = Utils.create_bosses()
				# regenerate_mp
				if now_min == 0 and now_sec >= 0 and now_sec < 6 and self.last_hour_mp != now_hour:
					self.last_hour_mp = now_hour
					for nick in self.players:
						self.players[nick]['mp'] = self.players[nick]['mmp']
					self.connection.privmsg(self.channel, "\x02One hour has passed, " +
						"and all players have their MP regenerated.\x02")
				# show/hide bosses
				for i in range(2):
					if Utils.bosses:
						if now_hour == Utils.bosses[i]['h'] and now_min == Utils.bosses[i]['m'] and \
						now_sec >= Utils.bosses[i]['s'] and now_sec < Utils.bosses[i]['s'] + 10 and not Utils.bosses[i]['on']:
							Utils.bosses[i]['on'] = True
							self.connection.privmsg(self.channel, self.msg_boss_join[i])
							self.connection.privmsg(self.channel, self.msg_boss_name[i] +
								random.choice(self.msg_boss_taunt[i]))
						if now_hour == Utils.bosses[i]['h'] and now_min == Utils.bosses[i]['m'] + 15 and \
						now_sec >= Utils.bosses[i]['s'] and now_sec <= Utils.bosses[i]['s'] + 10:
							if Utils.bosses[i]['on']:
								Utils.bosses[i]['on'] = False
								Utils.bosses[i]['shown'] = True
								self.connection.privmsg(self.channel, self.msg_boss_leave[i])
			time.sleep(5)

	def give_bonus(self):
		while self.loop:
			if len(self.players) > 1:
				now_hour = datetime.datetime.now().hour
				now_min = datetime.datetime.now().minute
				now_sec = datetime.datetime.now().second
				if now_min == 1 and now_sec >= 0 and now_sec < 10 and self.last_hour_bonus != now_hour:
					self.last_hour_bonus = now_hour
					if Schedule.is_bonus_on:
						self.connection.privmsg(self.channel, "Bonus temporary effects have now disappeared.")
						self.clear_bonus()
						Schedule.is_bonus_on = False
					if now_hour % 3 == 0: #every 3 hours
						# types of bonuses: 0 for nothing, 1 for +30%, 2 for -30%, 3 for 1 & 2
						# probab of choosing bonuses: 0: 10%, 1: 40%, 2: 40%, 3: 10%
						bonus_types = [0] + [1] * 4 + [2] * 4 + [3]
						bonus_choice = random.choice(bonus_types)
						if bonus_choice in (1, 2):
							Schedule.is_bonus_on = True
							list_nicks = self.bonus_random_players(bonus_choice)
							self.connection.privmsg(self.channel, self.bonus_texts[bonus_choice - 1].
								format(random.choice(self.bonus_vars[bonus_choice - 1])))
							self.connection.privmsg(self.channel, "\x02" + list_nicks + "\x02")
						elif bonus_choice == 3:
							Schedule.is_bonus_on = True
							[list_nicks1, list_nicks2] = self.bonus_random_players(3)
							self.connection.privmsg(self.channel, self.bonus_texts[0].format(
								random.choice(self.bonus_vars[0])))
							self.connection.privmsg(self.channel, "\x02" + list_nicks1 + "\x02")
							self.connection.privmsg(self.channel, self.bonus_texts[1].format(
								random.choice(self.bonus_vars[1])))
							self.connection.privmsg(self.channel, "\x02" + list_nicks2 + "\x02")
						else:
							pass # no bonus
					# save new stats after regenerate_mp and give_bonus
					self.dbc.save(self.players, self.profiles)
			time.sleep(5)

	def bonus_random_players(self, btype):
		nb_sample = math.ceil(0.1 * len(self.players))
		if btype in (1, 2):
			rand_sample = random.sample(list(self.players), nb_sample)
			list_nicks = ", ".join(rand_sample)
			for nick in rand_sample:
				User.set_bonus(nick, self.players, btype)
			list_nicks = list_nicks.replace("..", "[").replace(",,", "]")
			return list_nicks
		else: # btype == 3
			half1 = random.sample(list(self.players), len(self.players) // 2)
			half2 = [nick for nick in self.players if nick not in half1]
			rand_sample1 = random.sample(half1, nb_sample)
			rand_sample2 = random.sample(half2, nb_sample)
			list_nicks1 = ", ".join(rand_sample1)
			list_nicks2 = ", ".join(rand_sample2)
			for nick in rand_sample1:
				User.set_bonus(nick, self.players, 1)
			for nick in rand_sample2:
				User.set_bonus(nick, self.players, 2)
			list_nicks1 = list_nicks1.replace("..", "[").replace(",,", "]")
			list_nicks2 = list_nicks2.replace("..", "[").replace(",,", "]")
			return [list_nicks1, list_nicks2]

	def clear_bonus(self):
		for nick in self.players:
			User.set_bonus(nick, self.players, 0)

	def stop(self):
		self.loop = False
