import pymysql

class Database:
	def __init__(self):
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

	def query(self, expr):
		try:
			self.cur.execute(expr)
		except Exception as err:
			print("Error: {}".format(err))
			raise

	def is_registered(self, nick):
		res = self.query("select from users where nick='{}'".format(nick))
		if res:
			return True

	def register_user(self, nick, usertype, main_nick=None):
		if not self.is_registered(nick):
			if not main_nick:
				main_nick = nick
			self.query("insert into `users` values ('', '{0}', '{1}', '{2}', 0)".format(
			nick, main_nick, usertype))
