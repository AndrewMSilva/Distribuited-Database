from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from threading import Thread
import hashlib
import time
import pickle

class Service(object):
	# Host settings
	_IP   = None
	_Port = 5918
	# Control settings
	__Running = False
	__Socket  = None
	_Timeout  = 1
	# Authentication settings
	__PrivateKey = None
	__PublicKey  = None
	# Message settings
	__BufferLength = 8*1024

	def __init__(self, private_key, public_key):
		# Hashing keys
		self.__PrivateKey = hashlib.sha1(private_key.encode('latin1')).hexdigest()
		self.__PublicKey = hashlib.sha1(public_key.encode('latin1')).hexdigest()
		super().__init__()
	
	def _NewSocket(self):
		return socket(AF_INET, SOCK_STREAM)

	def _StartService(self):
		# Getting local IP
		s = socket(AF_INET, SOCK_DGRAM)
		try:
			s.connect(('10.255.255.255', 1))
			self._IP = s.getsockname()[0]
		except:
			self._IP = '127.0.0.1'
		finally:
			s.close()
		# Binding socket
		self.__Socket = self._NewSocket()
		try:
			self.__Socket.bind((self._IP, self._Port))
			print('Listening in', self._IP+':'+str(self._Port))
			self.__Running = True
			listener = Thread(target=self.__Listener)
			listener.start()
		except Exception as e:
			print(e)
			return
	
	def __Listener(self):
		if not self.__Socket: return
		self.__Socket.settimeout(self._Timeout)
		self.__Socket.listen(1)
		while self.__Running:
			try:
				conn, addr = self.__Socket.accept()
				connection = Thread(target=self._Connection, args=[conn,])
				connection.start()
			except:
				pass
		self.__Socket.close()

	# Thread of connections
	def _Connection(self, conn):
		conn.settimeout(self._Timeout)
		waiting_message = True
		while waiting_message:
			message = self._Receive(conn)
			if not message:
				break
			elif message == TimeoutError:
				continue
			waiting_message = False
			private = message['key'] == self.__PrivateKey
			self.HandleMessage(conn, message, private)

		conn.close()
	
	# Enconding a message
	def _EncodeMessage(self, data, type, private=False):
		message = {'type': type, 'time_stamp': time.time(), 'data': data}
		if private:
			message['key'] = self.__PrivateKey
		else:
			message['key'] = self.__PublicKey
		return pickle.dumps(message)
	
	# Receiving and authenticating a message
	def _Receive(self, conn):
		try:
			receiving = True
			enconded_message = b''
			message = None
			while receiving:
				packet = conn.recv(self.__BufferLength)
				if not packet:
					receiving = False
				else:
					enconded_message += packet
					try:
						message = pickle.loads(enconded_message)
						receiving = False
					except:
						continue

			if isinstance(message, dict) and 'key' in message and 'type' in message and 'time_stamp' in message and 'data' in message and (message['key'] == self.__PrivateKey or message['key'] == self.__PublicKey):
				return message
			else:
				return None
		except TimeoutError:
			print('Message timeout')
			return None
		else:
			return None			
	
	# This function will do something with the received messages, thus need to be overrided
	def HandleMessage(self, conn, message, private):
		pass

	def IsRunning(self):
		return self.__Running

	def Close(self):
		self.__Running = False