from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from threading import Thread
import hashlib
import time
import json

class Service(object):
	# Host settings
	_IP   = None
	_Port = 5918
	# Control settings
	__Running = False
	__Socket  = None
	__Group	  = {}
	__Connections = {}
	__Timeout     = 0.1
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
	
	def _Socket(self):
		return socket(AF_INET, SOCK_DGRAM)

	def Bind(self):
		# Getting local IP
		s = self._Socket()
		try:
			s.connect(('10.255.255.255', 1))
			self._IP = s.getsockname()[0]
		except:
			self._IP = '127.0.0.1'
		finally:
			s.close()
		# Binding socket
		self.__Socket = socket(AF_INET, SOCK_STREAM)
		try:
			self.__Socket.bind((self._IP, self._Port))
			print('Listening in', self._IP+':'+str(self._Port))
			self.__Running = True
		except Exception as e:
			print(e)
			return
	
	# Listening to new connections
	def Listen(self):
		listener = Thread(target=self.__Listener)
		listener.start()
	
	def __Listener(self):
		if not self.__Socket: return
		self.__Socket.settimeout(self.__Timeout)
		self.__Socket.listen(1)
		while self.__Running:
			try:
				conn, addr = self.__Socket.accept()
				i = len(self.__Connections)
				if addr[0] in self.__Connections:
					conn.close()
					continue
				self.__Connections[addr[0]] = {'private': False, 'conn': conn}
				connection = Thread(target=self._Connection, args=[addr[0],])
				connection.start()
			except:
				pass
		self.__Socket.close()

	# Thread of connections
	def _Connection(self, ip):
		self.__Connections[ip].conn.settimeout(self.__Timeout)
		while self.__Running:
			try:
				message = self._Receive(self.__Connections[ip].conn)
				if not message:	break
				self._HandleMessage(self.__Connections[ip].conn, message)
			except:
				pass
			
		conn.close()
	
	# Enconding a message
	def _EncodeMessage(self, data, type, private=False):
		message = {'type': type,'time_stamp': time.time(), 'data': data}
		if private:
			message['key'] = self.__PrivateKey
		else:
			message['key'] = self.__PublicKey
		return json.dumps(message)
	
	# Receiving and authenticating a message
	def _Receive(self, conn):
		enconded_message = conn.recv(self.__BufferLength)
		message = json.loads(enconded_message.decode('latin1'))
		if 'key' in message and 'time_stamp' in message and 'data' in message:
			if message.key != self.__PrivateKey and message.key != self.__PublicKey:
				return
			elif message.key == self.__PrivateKey:
				self.__Connections[ip].private = True
			elif message.key == self.__PublicKey:
				self.__Connections[ip].private = False
			return message					
		else:
			return
	
	# Handling a received message (need to be overrided)
	def HandleMessage(self, conn, message):
		pass
	
	def IsRunning(self):
		return self.__Running

	def Close(self):
		self.__Running = False