class AdminCommand:
	def __init__(self, conn, dbc, channel):
		self.dbc = dbc
		self.connection = conn
		self.channel = channel

	def quit(self, message=None):
		if message:
			self.connection.disconnect(message)
		else:
			self.connection.disconnect("I am going away to fill up my tanks. I will be back soon.")
		self.dbc.disconnect()
		print("Zombire bot has exited successfully.")
		exit(0)

	def execute(self, command):
		command = command.strip()
		first_space = command.find(" ")
		if first_space == -1:
			cmd = command.lower()
			args = ""
		else:
			cmd = command[0:first_space].lower()
			args = command[first_space:].lstrip()
		if cmd == "quit":
			self.quit(args)
