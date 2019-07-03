from Controller import Controller

server = Controller("Aa@Si12!", "2fT1@ds?")
server.Start()

if server.IsRunning():
	print('Ready for commands')
	
while server.IsRunning():
	query = input()
	try:
		splited = query.lower().split()
	except:
		splited = None
	if query.lower() == 'close':
		server.Close()
	elif splited and len(splited) == 2 and splited[0] == 'invite':
		server.ShowResult(server.Invite(splited[1]))
	elif splited and len(splited) == 2 and splited[0] == 'exit' and splited[1] == 'group':
		server.ShowResult(server.ExitGroup())
	elif query != '':
		server.ShowResult(server.Execute(query))