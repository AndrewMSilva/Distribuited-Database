from StorageManager import StorageManager
import Validator
import sqlparse
import time

class Controller(StorageManager):
	_QueryMessage = 'query'
	# Result status
	__ErrorStatus   = 'Error'
	__SuccessStatus = 'Success'

	def Start(self):
		self._StartService()
		self._InitializeGroup()
		self._InitializeStorage()

	def HandleMessage(self, conn, message, private):
		result = None
		# Executing requisition
		if message['type'] == self._QueryMessage:
			result = self.Execute(query)
		elif private:
			if message['type'] == self._InviteMessage or message['type'] == self._ExitMessage:
				old_group = self._UpdateGroup(message['data']['group'])
				if isinstance(message['data']['storage'], list):
					self._OverrideStorage(message['data']['storage'])
				self._RedistributeFiles(old_group)
			elif message['type'] == self._InsertFileMessage:
				self._InsertFile(message['data']['pointer'], message['data']['file_name'], False)
			elif message['type'] == self._CreateMetaPageMessage:
				result = self._CreateMetaPage(message['data']['table_name'], message['data']['fields'])
			elif message['type'] == self._CreatePageMessage:
				result = self._CreatePage(message['data']['table_name'], message['data']['offset'])
			elif message['type'] == self._GetMetaMessage:
				result = self._GetMeta(message['data']['table_name'])
			elif message['type'] == self._CreateFrameMassege:
				result = self._CreateFrame(message['data']['table_name'], message['data']['offset'], message['data']['values'])
			elif message['type'] == self._RedistributeMessage:
				self._SaveFile(message['data']['file_name'], message['data']['content'])
		# Sending result
		if not result is None:
			enconded_message = self._EncodeMessage(result, result, True)
			conn.send(enconded_message)

	def ExitGroup(self):
		start_time = time.time()
		old_group = self._ExitGroup()
		if old_group:
			self._RedistributeFiles(old_group)
			self._ClearStorage()
		return self.__Result(self.__SuccessStatus, start_time)

	# Creating a result
	def __Result(self, status, start_time, data=[]):
		if not isinstance(data, list):
			data = [data]
		return {'status': status, 'duration': time.time()-start_time, 'data': data}
	
	# Showing a result
	def ShowResult(self, result):
		print()
		print('Status:', result['status'])
		print('Duration:', result['duration'])
		for element in result['data']:
			print(element)
		print()
	
	def Invite(self, ip):
		start_time = time.time()
		result = self._Invite(ip, self._Storage)
		return self.__Result(result, start_time)

	# Executing a query
	def Execute(self, query):
		query = sqlparse.format(query, reindent=True, keyword_case='upper')
		stmt = sqlparse.parse(query)
		stmt = stmt[0]
		function = stmt.get_type()
		if function == "CREATE":
			return self.__CreateTable(stmt)
		elif function == "INSERT":
			return self.__InsertInto(stmt)
		else:
			return self.__Result('Command not found', time.time())
	
	def __CreateTable(self, stmt):
		start_time = time.time()
		args = Validator.CreateTable(stmt, self._Integer, self._Char, self._Varchar)
		if not args:
			return self.__Result(self.__ErrorStatus, start_time, 'Sintax error')
		
		table_name = args[0]
		fields = args[1:]
		# Creating pages
		if(self._CreateMetaPage(table_name, fields)):
			self._CreatePage(table_name, 0)
			return self.__Result(self.__SuccessStatus, start_time)
		else:
			return self.__Result(self.__ErrorStatus, start_time, 'Table already exists')

	def __InsertInto(self, stmt):
		start_time = time.time()
		args = Validator.InsertInto(stmt)
		if not args:
			return self.__Result(self.__ErrorStatus, start_time, 'Sintax error')

		table_name = args[0]
		values = args[1:]
		offset = 0
		if(self._FileExists(self._Page(table_name, self._MetaData))):
			result = self._CreateFrame(table_name, offset, values)
			if isinstance(result, str):
				return self.__Result(self.__ErrorStatus, start_time, result)
			elif not result:
				return self.__Result(self.__ErrorStatus, start_time, 'Internal error')
			else:
				return self.__Result(self.__SuccessStatus, start_time)
		else:
			return self.__Result(self.__ErrorStatus, start_time, 'Table not found')