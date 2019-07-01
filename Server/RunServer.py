from Controller import Controller

server = Controller("Aa@Si12!", "2fT1@ds?")
server.Start()

while server.IsRunning():
	query = input('> ')
	try:
		splited = query.lower().split()
	except:
		splited = None
	if query.lower() == 'close':
		server.Close()
	elif splited and splited[0] == 'invite' and len(splited) == 2:
		server.ShowResult(server.Invite(splited[1]))
	elif query != '':
		server.ShowResult(server.Execute(query))