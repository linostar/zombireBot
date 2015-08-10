import random

from .utils import Utils


class User:
	CUMULATIVE = 5
	MMP_MAX = 60
	MMP_MIN = 1
	rare_items = (7, 8, 9, 10, 11, 12, 13, 14)
	item_names = {
	0: "",
	1: "small apple",   # +2 HP
	2: "medium apple",  # +5 HP
	3: "large apple",   # +10 HP
	4: "small lemon",   # +1 MP
	5: "medium lemon",  # +2 MP
	6: "large lemon",   # +3 MP
	7: "Tansformic",    # for type transformation
	8: "Explodic",      # for a suicidal attack
	9: "Neutralic",     # for removing bonus effect
	10: "Switchic",     # for switching HP stats with another player
	11: "Drainic",        # sacrifice 1 MP to get 5 HP
	}

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
	def transform(target, players, source=None):
		if players[target]['hp'] > 0:
			return False
		if players[target]['type'] == "v":
			players[target]['type'] = "z"
		else:
			players[target]['type'] = "v"
		players[target]['hp'] = 10
		if source:
			players[source]['score'] += 5
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
		# check for bosses presence
		if Utils.bosses:
			if Utils.bosses[0]['on']:
				if p1['type'] == "v":
					dice1 = random.choice((5, 6))
				else:
					dice2 = random.choice((5, 6))
			if Utils.bosses[1]['on']:
				if p1['type'] == "z":
					dice1 = random.choice((5, 6))
				else:
					dice2 = random.choice((5, 6))
		diff_dice = dice1 - dice2
		players[source]['hp'] += diff_dice
		players[target]['hp'] -= diff_dice
		players[source]['mp'] -= 1
		if diff_dice > 0:
			players[source]['score'] += 2
		if players[source]['hp'] < 0:
			players[target]['hp'] += players[source]['hp']
			if diff_dice > 0:
				diff_dice += players[source]['hp']
			else:
				diff_dice -= players[source]['hp']
			players[source]['hp'] = 0
		if players[target]['hp'] < 0:
			players[source]['hp'] += players[target]['hp']
			if diff_dice > 0:
				diff_dice += players[target]['hp']
			else:
				diff_dice -= players[target]['hp']
			players[target]['hp'] = 0
		return [dice1, dice2, diff_dice]

	@staticmethod
	def ambush(source, target1, target2, players):
		random.seed()
		p0 = players[source]
		p1 = players[target1]
		p2 = players[target2]
		if p0['bonus'] % 10 == 1:
			dice0 = random.randint(3, 6) + random.randint(3, 6)
		elif p0['bonus'] % 10 == 2:
			dice0 = random.randint(1, 4) + random.randint(1, 4)
		else:
			dice0 = random.randint(1, 6) + random.randint(1, 6)
		if p1['bonus'] % 10 == 1:
			dice1 = random.randint(3, 6)
		elif p1['bonus'] % 10 == 2:
			dice1 = random.randint(1, 4)
		else:
			dice1 = random.randint(1, 6)
		if p2['bonus'] % 10 == 1:
			dice2 = random.randint(3, 6)
		elif p2['bonus'] % 10 == 2:
			dice2 = random.randint(1, 4)
		else:
			dice2 = random.randint(1, 6)
		# check for bosses presence
		if Utils.bosses:
			if Utils.bosses[0]['on']:
				if p0['type'] == "v":
					dice0 = random.choice((5, 6)) + random.choice((5, 6))
				else:
					dice1 = random.choice((5, 6))
					dice2 = random.choice((5, 6))
			if Utils.bosses[1]['on']:
				if p0['type'] == "z":
					dice0 = random.choice((5, 6)) + random.choice((5, 6))
				else:
					dice1 = random.choice((5, 6))
					dice2 = random.choice((5, 6))
		# check for ambush result
		players[source]['mp'] -= 2
		diff_dices = dice0 - dice1 - dice2
		if diff_dices > 0:
			players[source]['score'] += 3
			players[source]['hp'] += 6
			players[target1]['hp'] = max(players[target1]['hp'] - 3, 0)
			players[target2]['hp'] = max(players[target2]['hp'] - 3, 0)
		elif diff_dices < 0:
			players[source]['hp'] -= 6
			players[target1]['hp'] += 3
			players[target2]['hp'] += 3
		return diff_dices

	@staticmethod
	def challenge_boss(source, players):
		random.seed()
		p = players[source]
		if p['type'] == "v" and Utils.bosses[0]['on']:
			dice1 = random.choice((5, 6))
		elif p['type'] == "z" and Utils.bosses[1]['on']:
			dice1 = random.choice((5, 6))
		elif p['bonus'] % 10 == 1:
			dice1 = random.randint(3, 6)
		elif p['bonus'] % 10 == 2:
			dice1 = random.randint(1, 4)
		else:
			dice1 = random.randint(1, 6)
		dice2 = random.randint(1, 12)
		diff_dice = dice1 - dice2
		players[source]['mp'] -= 1
		players[source]['hp'] += diff_dice
		if diff_dice > 0:
			players[source]['score'] += 10
		elif diff_dice < 0:
			if players[source]['hp'] < 0:
				diff_dice -= players[source]['hp']
				players[source]['hp'] = 0
		return [diff_dice, dice1, dice2]

	@staticmethod
	def redetermine_mmp(result, nick, players):
		if result > 0:
			players[nick]['bonus'] -= (players[nick]['bonus'] // 100) * 100
			players[nick]['bonus'] += 10
			if (players[nick]['bonus'] % 100) // 10 == User.CUMULATIVE:
				players[nick]['bonus'] -= User.CUMULATIVE * 10
				if players[nick]['mmp'] < User.MMP_MAX:
					players[nick]['mmp'] += 1
					return 1
		elif result < 0:
			players[nick]['bonus'] -= ((players[nick]['bonus'] % 100) // 10) * 10
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
	def get_inventory(source, profiles):
		# lowest 12 bits of extras, since each item is 4 bits
		items = []
		inventory = profiles[source]['extras'] & 4095
		for i in range(3):
			items.append((inventory >> 4*i) & 15)
		return items

	@staticmethod
	def save_inventory(items, source, profiles):
		inventory = 0
		for i in range(3):
			inventory += items[i] * (16**i)
		profiles[source]['extras'] &= ~4095
		profiles[source]['extras'] |= inventory

	@staticmethod
	def search_item(source, profiles):
		random.seed()
		# 25% chance for finding an item
		chance = random.randint(1, 4)
		if chance == 2:
			return random.randrange(1, len(User.item_names))
		else:
			return 0

	@staticmethod
	def add_item(source, profiles, players):
		items = User.get_inventory(source, profiles)
		if items[0] and items[1] and items[2]:
			return -1  # inventory is full
		players[source]['mp'] -= 1
		new_item = User.search_item(source, profiles)
		if new_item:
			# don't allow a player to have more than 1 unit of a rare item
			while (new_item in User.rare_items and new_item in items) or not new_item:
				new_item = User.search_item(source, profiles)
			if items[0] and items[1]:
				items[2] = new_item
			elif items[0]:
				items[1] = new_item
			else:
				items[0] = new_item
			User.save_inventory(items, source, profiles)
			return new_item

	@staticmethod
	def get_item(item_index, source, profiles):
		return (User.get_inventory(source, profiles))[item_index]

	@staticmethod
	def drop_item(item_index, source, profiles):
		items = User.get_inventory(source, profiles)
		if item_index == 0:
			items[0] = items[1]
			items[1] = items[2]
			items[2] = 0
		elif item_index == 1:
			items[1] = items[2]
			items[2] = 0
		else:
			items[2] = 0
		User.save_inventory(items, source, profiles)

	@staticmethod
	def use_item(item, source, players):
		if item == 1:
			players[source]['hp'] += 2
		elif item == 2:
			players[source]['hp'] += 5
		elif item == 3:
			players[source]['hp'] += 10
		elif item == 4:
			players[source]['mp'] = min(players[source]['mp'] + 1, players[source]['mmp'])
		elif item == 5:
			players[source]['mp'] = min(players[source]['mp'] + 2, players[source]['mmp'])
		elif item == 6:
			players[source]['mp'] = min(players[source]['mp'] + 3, players[source]['mmp'])
		elif item == 7:
			if players[source]['type'] == "v":
				players[source]['type'] = "z"
			else:
				players[source]['type'] = "v"

	@staticmethod
	def use_item2(item, source, target, players):
		if item == 8:
			players[source]['hp'] = 1
			players[target]['hp'] = 1
		elif item == 9:
			players[target]['bonus'] = players[target]['bonus'] // 10 * 10
		elif item == 10:
			old_hp = players[source]['hp']
			players[source]['hp'] = players[target]['hp']
			players[target]['hp'] = old_hp
		elif item == 11:
			players[source]['mp'] -= 1
			players[target]['hp'] = max(players[target]['hp'] - 5, 0)

	@staticmethod
	def check_if_round_ended(players):
		len_vamp = len([nick for nick in players if players[nick]['type'] == "v"])
		if len(players) > 0:
			if (not len_vamp) or len_vamp == len(players):
				return max(players, key=lambda nick: players[nick]['score'])

	@staticmethod
	def reset_players(players):
		players.clear()
