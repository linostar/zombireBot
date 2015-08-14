import random
import math
import datetime


class Utils:
	VERSION = "1.3.4"
	MAX_MSG_LENGTH = 220
	HOW_TO_PLAY = "https://linostar.github.io/zombireBot"
	round_starttime = datetime.datetime.now()
	cs_list = 0
	#reg_list1 = []
	#reg_list2 = []
	registering_nick = ""
	# Dracula is bosses[0] and Zombilo is bosses[1]
	bosses = []
	b_created = False # for boss creation

	@staticmethod
	def cut_to_chunks(msg):
		if len(msg) <= Utils.MAX_MSG_LENGTH:
			return [msg]
		else:
			pos = 0
			msgs = []
			for i in range(math.ceil(len(msg)/Utils.MAX_MSG_LENGTH)):
				if pos + Utils.MAX_MSG_LENGTH > len(msg) - 1:
					last_space = msg.rfind(" ", pos, len(msg) - 1)
				else:
					last_space = msg.rfind(" ", pos, pos + Utils.MAX_MSG_LENGTH)
				msg.append(msg[pos:last_space])
				pos = last_space + 1
			return msgs

	@staticmethod
	def create_bosses():
		random.seed()
		leaders = []
		for i in (0, 1):
			hour = random.randint(0, 23)
			minute = random.randint(2, 44)
			second = random.randint(0, 59)
			leaders.append({'h': hour, 'm': minute, 's': second, 'on': False, 'shown': False})
		return leaders
