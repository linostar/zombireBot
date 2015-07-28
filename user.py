import random

class User:
	@staticmethod
	def is_online(conn, nick):
		conn.whois(nick)

	@staticmethod
	def is_identified(conn, nick):
		conn.privmsg("nickserv", "status {}".format(nick))

	@staticmethod
	def ratio_of_types(players):
		num_v = 0
		num_z = 0
		num_v = sum(num_v + 1 for nick in players if players[nick]['type'] == "v")
		num_z = sum(num_z + 1 for nick in players if players[nick]['type'] == "z")
		if num_v or num_z:
			return num_v / (num_v + num_z)
		return 0.5

	@staticmethod
	def transform(nick, players):
		if players[nick.lower()]['hp'] > 0:
			return False
		if players[nick.lower()]['type'] == "v":
			players[nick.lower()]['type'] = "z"
		else:
			players[nick.lower()]['type'] = "v"
		players[nick.lower()]['hp'] = 10
		return True

	@staticmethod
	def donate(source, target, players):
		players[source.lower()]['hp'] -= 2
		players[target.lower()]['hp'] += 1
		players[source.lower()]['mp'] -= 1

	@staticmethod
	def battle(source, target, players):
		random.seed()
		p1 = players[source.lower()]
		p2 = players[target.lower()]
		if p1['bonus'] % 10 == 1:
			dice1 = int(random.random() * 4) + 3 # +20% winning chance
		elif p1['bonus'] % 10 == 2:
			dice1 = int(random.random() * 4) + 1 # -20% winning chance
		else:
			dice1 = int(random.random() * 6) + 1 # normal winning chance
		if p2['bonus'] % 10 == 1:
			dice2 = int(random.random() * 4) + 3 # +20% winning chance
		elif p2['bonus'] % 10 == 2:
			dice2 = int(random.random() * 4) + 1 # -20% winning chance
		else:
			dice2 = int(random.random() * 6) + 1 # normal winning chance
		diff_dice = dice1 - dice2
		players[source.lower()]['hp'] += diff_dice
		players[target.lower()]['hp'] -= diff_dice
		players[source.lower()]['mp'] -= 1
		if diff_dice > 0:
			players[source.lower()]['score'] += 1
		return [dice1, dice2, diff_dice]
