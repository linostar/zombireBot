import threading
import datetime
import time

class Schedule:
	loop = True
	last_hour = -1

	def __init__(self, conn, channel, players):
		self.connection = conn
		self.channel = channel
		self.players = players
		regenerate_thread = threading.Thread(target=self.regenerate_mp)
		regenerate_thread.start()

	def regenerate_mp(self):
		while self.loop:
			now_hour = datetime.datetime.now().hour
			now_min = datetime.datetime.now().minute
			now_sec = datetime.datetime.now().second
			if now_min == 0 and now_sec >= 0 and now_sec < 6 and self.last_hour != now_hour:
				self.last_hour = now_hour
				for nick in self.players:
					self.players[nick]['mp'] = self.players[nick]['mmp']
				self.connection.privmsg(self.channel, "\x02One hour has passed, " +
					"and all players have their MP regenerated.\x02")
			time.sleep(5)

	def stop(self):
		self.loop = False
