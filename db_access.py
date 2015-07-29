import pymysql

class Database:
	def __init__(self, config):
		self.config = config
		self.connect()

	def connect(self):
		try:
			dbconf = self.config['db']
			self.conn = pymysql.connect(host=dbconf['host'], port=dbconf['port'], user=dbconf['user'],
			passwd=dbconf['pass'], db=dbconf['database'])
			self.cur = self.conn.cursor()
		except Exception as err:
			print("Error: {}".format(err))
			raise

	def disconnect(self):
		try:
			self.cur.close()
			self.conn.close()
		except pymysql.err.OperationalError as e:
			if e[0] == 2013:
				pass # sql connection already lost, nothing to close
		except Exception as err:
			print("Error: {}".format(err))
			raise

	def save(self, players):
		for nick in players:
			p = players[nick]
			self.query(("update `users` set `type` = '{p[type]}', `hp` = {p[hp]}, `mmp` = {p[mmp]}, " +
				"`score` = {p[score]}, `bonus` = {p[bonus]} where `nick` = '{nick}'").format(p=p, nick=nick))
		return True

	def query_select(self, expr, args=None):
		try:
			return self.cur.execute(expr, (args))
		except pymysql.err.OperationalError as e:
			if e[0] == 2013:
				self.connect()
		except Exception as err:
			print("Error: {}".format(err))
			raise

	def query(self, expr):
		try:
			self.cur.execute(expr)
		except pymysql.err.OperationalError as e:
			if e[0] == 2013:
				self.connect()
		except Exception as err:
			print("Error: {}".format(err))
			raise

	def is_registered(self, nick):
		if self.query_select("select * from `users` where `nick` = %s", nick.lower()):
			return True

	def register_user(self, nick, usertype, main_nick=None):
		if not self.is_registered(nick):
			if not main_nick:
				main_nick = nick
			self.query("insert into `users` values (0, '{0}', '{1}', '{2}', 10, 6, 0, 0)"
				.format(nick.lower(), main_nick.lower(), usertype))
			return True

	def unregister_user(self, nick):
		if self.is_registered(nick):
			self.query("delete from `users` where `nick` = '{}'".format(nick.lower()))
			return True

	def get_status(self, nick):
		if self.query_select("select `type`, `hp`, `mmp`, `score`, `bonus` from `users` where `nick` = %s", 
			(nick.lower())):
			for row in self.cur:
				return row

	def get_players(self):
		players = {}
		if self.query_select("select `nick`, `type`, `hp`, `mmp`, `score`, `bonus` from `users`", (None)):
			for row in self.cur:
				if row:
					players[row[0]] = {'type': row[1], 'hp': row[2], 'mp': row[3], 
					'mmp': row[3], 'score': row[4], 'bonus': row[5]}
		return players
