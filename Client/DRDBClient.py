from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
from threading import Thread
import hashlib
import time
import json

class DSQLiteClient():
	# Host settings
	__Port = 5918
	# Control settings
	__Running = False
	__Socket  = None
	__Connections = {}
	__Timeout     = 0.1
	# Authentication settings
	__Key = None
	# Message settings
	__BufferLength = 1024
	__QueryType    = 0
	__ResponseType = 1

	def __init__(self, ip, key):
		# Hashing keys
		self.__Key = hashlib.sha1(key.encode('latin1')).hexdigest()
		self.__Socket = socket(AF_INET, SOCK_STREAM)
		try:
			self.__Socket.connect((ip, self.__Port))
			self.__Running = True
		except:
			return None
	
	def IsRunning(self):
		return self.__Running
	
	# Enconding a message
	def __EncodeMessage(self, data, type=__QueryType, private=False):
		message = {'type': type,'time_stamp': time.time(), 'key': self.__Key, 'data': data}
		return json.dumps(message.decode('latin1'))
	
	def Execute(self, query):
		try:
			self.__Socket.send(self.__EncodeMessage(query))
		except:
			pass
	
	def Close(self):
		self.__Socket.close()
		self.__Running = False