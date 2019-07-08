from threading import Lock
from Service import Service
import pickle

class GroupManager(Service):
	# Group settings
	_Group = []
	__GroupLock = Lock()
	# Message types
	_InviteMessage  = 'invite'
	_ExitMessage	= 'exit'
	# Configs settings
	_ConfigsDirectory = './Configs/'
	__GroupConfigs	   = 'Group.config'

	def _InitializeGroup(self):
		if not self.__GetGroup():
			self._Group = [self._IP]
			self.__SaveGroup()
	
	def __GetGroup(self):
		try:
			file = open(self._ConfigsDirectory+self.__GroupConfigs, 'rb')
			group = pickle.load(file)
			file.close()
			self._Group = group.copy()
			if not self._IP in self._Group:
				print('Local IP not found in', self.__GroupConfigs)
				return False
			return True
		except:
			return False

	def __SaveGroup(self):
		try:
			file = open(self._ConfigsDirectory+self.__GroupConfigs, 'wb')
			pickle.dump(self._Group, file)
			file.close()
			print('Group updated')
			return True
		except:
			return False
	
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
		for ip in self._Group:
			if ip != self._IP:
				self._SendMessage(ip, data, type)

	def _Invite(self, ip, storage=None):
		# Verifying the connection is itself
		if ip == self._IP:
			return 'Unable to connect to itself'
		# Verifying if the connection already exists
		if ip in self._Group:
			return 'Already connected'
		# Sending invitation
		data = {'group': self._Group, 'storage': storage}
		result = self._SendMessage(ip, data, self._InviteMessage)
		if result:
			return 'Invitation sent'
		else:
			return 'Unable to connect'

	def _UpdateGroup(self, group, storage=None):
		# Using mutex to update group
		result = False
		self.__GroupLock.acquire()
		try:
			# Checking if the groups match
			if isinstance(group, list) and group != self._Group:
				# Creating a copy of the group before update it
				result = self._Group.copy()
				# Updateing group
				for ip in group:
					if not ip in self._Group:
						self._Group.append(ip)
				self._Group = sorted(self._Group)
				# Updating group
				self.__SaveGroup()
				# Sending the new group to other devices
				data = {'group': self._Group, 'storage': storage}
				self._GroupBroadcast(data, self._InviteMessage)
		except:
			result = False
		finally:
			self.__GroupLock.release()
			return result

	def _ExitGroup(self):
		result = False
		self.__GroupLock.acquire()
		try:
			old_group = self._Group.copy()
			self._Group = [self._IP]
			self.__SaveGroup()
			self._GroupBroadcast(self._IP, self._ExitMessage)
			result = old_group
		finally:
			self.__GroupLock.release()
			return result
	
	def _RemoveFromGroup(self, ip):
		result = self._Group.copy()
		self.__GroupLock.acquire()
		try:
			self._Group.remove(ip)
			self.__SaveGroup()
		except:
			result = None
		finally:
			self.__GroupLock.release()
			return result
		