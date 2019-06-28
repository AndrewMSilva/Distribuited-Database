from Controller import Controller

server = Controller("Aa@Si12!", "2fT1@ds?")
server.Bind()
server.Listen()

while server.IsRunning():
	query = input('> ')
	try:
		splited = query.lower().split()
	except:
		splited = None
	if query.lower() == 'close':
		server.Close()
	elif splited and splited[0] == 'include' and len(splited) == 2:
		server.Include(splited[1])
	else:
		server.Execute(query)