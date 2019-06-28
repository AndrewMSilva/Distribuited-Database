from Service import Service

class GroupManager(Service):
	# Group settings
	_ID    = 0
	_Group = {}
	# Message types
	__QueryMessage   = 'query'
	__IncludeMessage = 'include'
	__AgroupMessage  = 'agroup'

	def Bind(self):
		self._Bind()
		self._Group = {self._ID: self._IP}
	
	''' Group methods '''
	def __Agroup(self, ip, id=None, type=__AgroupMessage):
		# Verifying the connection is itself
		if ip == self._IP:
			print('Unable to connect to itself')
			return
		# Verifying if the connection already exists
		if ip in self._Group.values():
			print('IP already connected')
			return
		# Creating connection
		if self.__SendAgroupMessage(ip, type):
			if not id:
				id = len(self._Group)
			
			self._Group[id] = ip
			print('Connected to', str(id)+':'+ip)


	def __SendAgroupMessage(self, ip, type=__AgroupMessage):
		data = str(self._ID) + ':' + str(len(self._Group))
		for i in self._Group:
			if self._Group[i] != self._IP:
				data += ' ' + str(i) + ':' + self._Group[i]
		self._SendMessage(ip, data, type)

	def Include(self, ip):
		self.__Agroup(ip, type=self.__IncludeMessage)

	def _IncludeReceived(self, message):
		if message['type'] == self.__AgroupMessage or message['type'] == self.__IncludeMessage:
			# Verifying the new connection
			data = message['content'].split()[0].split(':')
			id = int(data[0])
			ip = addr[0]
			for i in self.__Group:
				if ip == self.__Group[i]:
					conn.close()
					continue
			# Creating a new connection
			self.__UpdateGroup(id, message['content'])
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
		s = self._Socket()
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