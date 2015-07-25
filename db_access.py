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
		except Exception as err:
			print("Error: {}".format(err))
			raise

	def query_select(self, expr, args=None):
		try:
			return self.cur.execute(expr, (args))
		except Exception as err:
			print("Error: {}".format(err))
			raise

	def query(self, expr):
		try:
			self.cur.execute(expr)
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
			self.query("insert into `users` values (0, '{0}', '{1}', '{2}', 0)".format(
			nick.lower(), main_nick.lower(), usertype))
			return True

	def get_status(self, nick):
		if self.query_select("select `type` from `users` where `nick` = %s", (nick.lower())):
			for row in self.cur:
				return row[0]
