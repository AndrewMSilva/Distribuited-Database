from Service import Service

class GroupManager(Service):
	# Group settings
	__ID   = 0
	_Group = {}
	# Message types
	__Query   = 0
	__Include = 1
	__Agroup  = 2

	def HandleMessage(self, message):
		print(message)
	
	''' Group methods '''
	def __Agroup(self, ip, id=None, type=__Agroup):
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


	def __SendAgroupMessage(self, ip, type=__Agroup):
		content = str(self.__ID) + ':' + str(len(self._Group))
		for i in self._Group:
			if self._Group[i] != self._IP:
				content += ' ' + str(i) + ':' + self._Group[i]

		enconded_message = self._EncodeMessage(type, content)
		try:
			s = socket(AF_INET, SOCK_STREAM)
			s.connect((ip, self._Port))
			s.send(enconded_message)
			s.close()
			return True
		except Exception as e:
			print('Error:', e)
			return False

	def Include(self, ip):
		self.__Agroup(ip, type=self.__Include)

	def _IncludeReceived(self, message):
		if message['Type'] == self.__Agroup or message['Type'] == self.__Include:
			# Verifying the new connection
			content = message['Content'].split()[0].split(':')
			id = int(content[0])
			ip = addr[0]
			for i in self.__Group:
				if ip == self.__Group[i]:
					conn.close()
					continue
			# Creating a new connection
			self.__UpdateGroup(id, message['Content'])
			if message['Type'] == Include:
				print('Connected to', ip)
				old_id = self.__ID
				del self._Group[old_id]
				self.__ID = int(content[1])
				self._Group[self.__ID] = LocalIP
				self.__SendAgroupMessage(ip)
			self._Group[id] = ip

	def __UpdateGroup(self, id, content):
		content = content.split()[1:]
		for addr in content:
			addr = addr.split(':')
			id = addr[0]
			ip = addr[1]
			if not ip in self._Group.values():
				self.__Agroup(ip, id)
