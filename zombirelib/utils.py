import math

class Utils:
	VERSION = "1.1.0"
	MAX_MSG_LENGTH = 220
	HOW_TO_PLAY = "https://linostar.github.io/zombireBot"
	cs_list = 0
	#reg_list1 = []
	#reg_list2 = []
	registering_nick = ""

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
