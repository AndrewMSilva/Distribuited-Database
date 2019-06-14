import Settings.Function as Function
import Modules.Communicator as Communicator
import Modules.Validator as Validator
import Modules.Controller as Controller

def Connection(conn, addr):
	message = Communicator.ReceiveMessage(conn)
	if message:
		cmd = Validator.Read(message['Content'])
		exec(cmd)
            
	conn.close()

# Starting service
TCP = Communicator.BindSocket()
if TCP:
	TCP.listen(1)
	while True:
		conn, addr = TCP.accept()
		connection = Thread(target=Connection, args=[conn, addr,])
		connection.start()
	TCP.close()