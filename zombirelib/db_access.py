import datetime

import pymysql

class Database:
	NUM_TOPSCORES = 10

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

	def save(self, players, profiles, arsenals):
		if not players:
			self.query("delete from `users`")
			return True
		for nick in players:
			p = players[nick]
			self.query(("update `users` set `type` = '{p[type]}', `hp` = {p[hp]}, `mmp` = {p[mmp]}, " +
				"`score` = {p[score]}, `bonus` = {p[bonus]} where `nick` = '{nick}'").format(p=p, nick=nick))
		for nick in profiles:
			p = profiles[nick]
			self.query("update `profiles` set `autovals` = {}, `extras` = {} where `nick` = '{}'"
				.format(p['auto'], p['extras'], nick))
		for nick in arsenals:
			a = arsenals[nick]
			self.query("update `arsenals` set `sword` = {}, `slife` = {}, `armor` = {}, `alife` = {} where `nick` = '{}'"
				.format(a['sword'], a['slife'], a['armor'], a['alife'], nick))
		return True

	def query_select(self, expr, args=None):
		try:
			self.conn.ping(reconnect=True)
			return self.cur.execute(expr, (args))
		except pymysql.err.OperationalError as e:
			if e[0] == 2013:
				self.connect()
		except Exception as err:
			print("Error: {}".format(err))
			raise

	def query(self, expr):
		try:
			self.conn.ping(reconnect=True)
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

	def has_profile(self, nick):
		if self.query_select("select * from `profiles` where `nick` = %s", nick.lower()):
			return True

	def has_arsenal(self, nick):
		if self.query_select("select * from `arsenals` where `nick` = %s", nick.lower()):
			return True

	def register_user(self, nick, usertype, main_nick=None):
		if not self.is_registered(nick):
			if not main_nick:
				main_nick = nick
			self.query("insert into `users` values (0, '{0}', '{1}', '{2}', 10, 5, 0, 0)"
				.format(nick.lower(), main_nick.lower(), usertype))
			if not self.has_profile(nick):
				self.query("insert into `profiles` values (0, '{}', 0, 0)"
					.format(nick.lower()))
			if not self.has_arsenal(nick):
				self.query("insert into `arsenals` values (0, '{}', 0, 0, 0, 0)"
					.format(nick.lower()))
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

	def get_profiles(self):
		profiles = {}
		if self.query_select("select `nick`, `autovals`, `extras` from `profiles`",	(None)):
			for row in self.cur:
				if row:
					profiles[row[0]] = {'auto': row[1], 'extras': row[2]}
		return profiles

	def get_arsenals(self):
		arsenals = {}
		if self.query_select("select `nick`, `sword`, `slife`, `armor`, `alife` from `arsenals`", (None)):
			for row in self.cur:
				if row:
					arsenals[row[0]] = {'sword': row[1], 'slife': row[2], 'armor': row[3], 'alife': row[4]}
		return arsenals

	def delete_profile(self, nick):
		self.query("delete from `profiles` where `nick` = '{}'".format(nick))

	def delete_arsenal(self, nick):
		self.query("delete from `arsenals` where `nick` = '{}'".format(nick))

	def add_highscore(self, nick, utype, score):
		now_date = datetime.date.today().strftime("%Y-%m-%d")
		self.query("insert into `highscores` values (0, '{0}', '{1}', {2}, '{3}')".format(
			nick, utype, score, now_date))

	def get_topscores(self):
		scores = []
		if self.query_select("select `nick`, `type`, `score` from `highscores` " + 
			"order by `score` desc limit %s", (Database.NUM_TOPSCORES)):
			for row in self.cur:
				if row:
					scores.append(row)
		return scores

	def get_admin_topscores(self):
		scores = []
		if self.query_select("select `nick`, `type`, `score`, `date` from `highscores` " +
			"order by `score` desc limit %s", (Database.NUM_TOPSCORES)):
			for row in self.cur:
				if row:
					scores.append(row)
		return scores

	def clear_scores(self):
		self.query("delete from `highscores`")
