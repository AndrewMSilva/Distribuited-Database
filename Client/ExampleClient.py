from ClientModule import ClientModule

client = ClientModule('172.20.66.48', '2fT1@ds?')
while client.IsRunning:
    query = input('> ')
    response = client.Execute(query)