from Controller import Controller

server = Controller("Aa@Si12!", "2fT1@ds?")
server.Bind()
server.Listen()

while server.IsRunning():
    query = input('> ')
    if query.lower() == 'close':
        server.Close()
    else:
        server.Execute(query)