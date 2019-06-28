from Service import Service

class GroupManager(Service):
	# Group settings
	_ID    = 0
	_Group = {}
	# Message types
	__QueryMessage   = 'query'
	__IncludeMessage = 'include'
	__AgroupMessage  = 'agroup'

	def Start(self):
		self._Start()
		self._Group = {self._ID: self._IP}
	
	''' Group methods '''
	def __Agroup(self, ip, id=None, type=__AgroupMessage):
		# Verifying the connection is itself
		if ip == self._IP:
			return 'Unable to connect to itself'
		# Verifying if the connection already exists
		if ip in self._Group.values():
			return 'Already connected'
		# Creating connection
		if self._SendMessage(ip, self._Group, type):
			if not id:
				id = len(self._Group)
			
			self._Group[id] = ip
			return 'Connected'
		else:
			return 'Unable to connect'
			
	def _Include(self, ip):
		return self.__Agroup(ip, type=self.__IncludeMessage)

	def _IncludeReceived(self, message):
		if message['type'] == self.__AgroupMessage or message['type'] == self.__IncludeMessage:
			group = message['data']
			# TO DO
			id = max(group.keys())+1
			for i in self.__Group:
				if ip == self.__Group[i]:
					conn.close()
					continue
			# Creating a new connection
			self.__UpdateGroup(id, message['data'])
			if message['type'] == Include:
				print('Connected to', ip)
				old_id = self._ID
				del self._Group[old_id]
				self._ID = int(data[1])
				self._Group[self._ID] = LocalIP
				self.__SendAgroupMessage(ip)
			self._Group[id] = ip

	def __UpdateGroup(self, id, data):
		data = data.split()[1:]
		for addr in data:
			addr = addr.split(':')
			id = addr[0]
			ip = addr[1]
			if not ip in self._Group.values():
				self.__Agroup(ip, id)

	def _SendMessage(self, ip, data, type, wait_result=False):
		enconded_message = self._EncodeMessage(data, type, True)
		s = self._NewSocket()
		result = True
		try:
			s.connect((ip, self._Port))
			s.send(enconded_message)
			if wait_result:
				result = self._Receive(s)
		except Exception as e:
			result = False
		finally:
			s.close()
			return result