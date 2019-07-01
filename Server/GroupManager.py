from threading import Lock
from Service import Service
import json

class GroupManager(Service):
	# Group settings
	_ID    = 0
	_Group = {}
	__GroupLock = Lock()
	# Message types
	_InviteMessage  = 'invite'
	# Configs settings
	_ConfigsDirectory = './Configs/'
	__GroupConfigs	   = 'Group.config'
	
	def _SendMessage(self, ip, data, type, wait_result=False):
		enconded_message = self._EncodeMessage(data, type, True)
		s = self._NewSocket()
		s.settimeout(self._Timeout)
		result = True
		try:
			s.connect((ip, self._Port))
			s.send(enconded_message)
			if wait_result:
				result = self._Receive(s)
		except:
			result = False
		finally:
			s.close()
			return result
	
	def _GroupBroadcast(self, data, type):
		for ip in self._Group.values():
			if ip != self._IP:
				self._SendMessage(ip, data, type)

	def _Invite(self, ip):
		# Verifying the connection is itself
		if ip == self._IP:
			return 'Unable to connect to itself'
		# Verifying if the connection already exists
		if ip in self._Group.values():
			return 'Already connected'
		# Sending invitation
		result = self._SendMessage(ip, self._Group, self._InviteMessage, True)
		if result:
			return 'Invitation sent'
		else:
			return 'Unable to connect'

	async def _UpdateGroup(self, message):
		# Using mutex to update group
		result = False
		await self.__GroupLock.acquire()
		try:
			group = message['data']
			# Checking if the groups match
			if group != self._Group:
				# Getting all ips
				ips = self._Group.values()
				for ip in group.values():
					if not ip in ips:
						ips.append(ip)
				ips = sort(ips)
				# Distributing ids
				group = {}
				for id in range(0, len(ips)):
					group[id] = ip
					if ip == self._IP:
						self._ID = id
				# Updating group
				self._Group = group.copy()
				self.__SaveGroup()
				# Return a copy of the old group
				result = self._Group.copy()
				# Sending the new group to other devices
				self._GroupBroadcast(self._Group, self._InviteMessage)
		except:
			result = False
		finally:
			self.__GroupLock.release()
			return result
	
	def __GetGroup(self):
		try:
			file = open(self._ConfigsDirectory+self.__GroupConfigs, 'r')
			group_json = file.read()
			file.close()
			self._Group = json.loads(group_json)
			return True
		except:
			return False

	def __SaveGroup(self):
		try:
			file = open(self._ConfigsDirectory+self.__GroupConfigs, 'w')
			group_json = json.dumps(self._Group)
			file.write(group_json)
			file.close()
			return True
		except:
			return False

	def _InitializeGroup(self):
		if not self.__GetGroup():
			self._Group = {self._ID: self._IP}
			self.__SaveGroup()