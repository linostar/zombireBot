import random

class User:
	CUMULATIVE = 5
	MMP_MAX = 60
	MMP_MIN = 1

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
		if players[nick]['hp'] > 0:
			return False
		if players[nick]['type'] == "v":
			players[nick]['type'] = "z"
		else:
			players[nick]['type'] = "v"
		players[nick]['hp'] = 10
		return True

	@staticmethod
	def donate(source, target, players):
		players[source]['hp'] -= 2
		players[target]['hp'] += 1
		players[source]['mp'] -= 1
		players[source]['score'] += 1

	@staticmethod
	def battle(source, target, players):
		random.seed()
		p1 = players[source]
		p2 = players[target]
		if p1['bonus'] % 10 == 1:
			dice1 = int(random.random() * 4) + 3 # +30% winning chance
		elif p1['bonus'] % 10 == 2:
			dice1 = int(random.random() * 4) + 1 # -30% winning chance
		else:
			dice1 = int(random.random() * 6) + 1 # normal winning chance
		if p2['bonus'] % 10 == 1:
			dice2 = int(random.random() * 4) + 3 # +30% winning chance
		elif p2['bonus'] % 10 == 2:
			dice2 = int(random.random() * 4) + 1 # -30% winning chance
		else:
			dice2 = int(random.random() * 6) + 1 # normal winning chance
		diff_dice = dice1 - dice2
		players[source]['hp'] += diff_dice
		players[target]['hp'] -= diff_dice
		players[source]['mp'] -= 1
		if diff_dice > 0:
			players[source]['score'] += 2
		if players[source]['hp'] < 0:
			players[target]['hp'] += players[source]['hp']
			diff_dice += players[source]['hp']
			players[source]['hp'] = 0
		if players[target]['hp'] < 0:
			players[source]['hp'] += players[target]['hp']
			diff_dice += players[target]['hp']
			players[target]['hp'] = 0
		return [dice1, dice2, diff_dice]

	@staticmethod
	def redetermine_mmp(result, nick, players):
		if result > 0:
			players[nick]['bonus'] += 10
			if (players[nick]['bonus'] % 100) // 10 == User.CUMULATIVE:
				players[nick]['bonus'] -= User.CUMULATIVE * 10
				if players[nick]['mmp'] < User.MMP_MAX:
					players[nick]['mmp'] += 1
					return 1
		elif result < 0:
			players[nick]['bonus'] += 100
			if players[nick]['bonus'] // 100 == User.CUMULATIVE:
				players[nick]['bonus'] -= User.CUMULATIVE * 100
				if players[nick]['mmp'] > User.MMP_MIN:
					players[nick]['mmp'] -= 1
					return -1
		else:
			# reset the cumulation to zero
			players[nick]['bonus'] %= 10

	@staticmethod
	def check_if_round_ended(players):
		len_vamp = len([nick for nick in players if players[nick]['type'] == "v"])
		if len(players) > 0:
			if (not len_vamp) or len_vamp == len(players):
				return max(players, key=lambda nick: players[nick]['score'])

	@staticmethod
	def reset_players(players):
		players.clear()
