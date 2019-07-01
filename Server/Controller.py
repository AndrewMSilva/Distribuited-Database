from StorageManager import StorageManager
import Validator
import sqlparse
import time

class Controller(StorageManager):
	_QueryMessage = 'query'

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
			if message['type'] == self._InviteMessage:
				old_group = self._UpdateGroup(message)
			elif message['type'] == self._CreateMetaPageMessage:
				result = self._CreateMetaPage(message['data']['table_name'], message['data']['fields'])
			elif message['type'] == self._CreatePageMesssage:
				result = self._CreatePage(message['data']['table_name'], message['data']['offset'])
			elif message['type'] == self._GetMetaMesssage:
				result = self._GetMeta(message['data']['table_name'])
			elif message['type'] == self._CreateFrameMassege:
				result = self._CreateFrame(message['data']['table_name'], message['data']['offset'])
		# Sending result
		if not result is None:
			enconded_message = self._EncodeMessage(result, self._Result, True)
			conn.send(enconded_message)

	# Creating a result
	def __Result(self, status, start_time, data=[]):
		return {'status': status, 'duration': time.time()-start_time, 'data': data}
	
	# Showing a result
	def ShowResult(self, result):
		print('Status:', result['status'])
		print('Duration:', result['duration'])
		for element in result['data']:
			print(element)
	
	def Invite(self, ip):
		start_time = time.time()
		return self.__Result(super()._Invite(ip), start_time)

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
		elif function == "DELETE":
			return self.__DeleteFrom(stmt)
		elif function == "SELECT":
			for i in range(0, len(stmt.tokens)):
				print(i, stmt.tokens[i])
			#Select()
		else:
			return self.__Result('Command not found', time.time())
	
	def __CreateTable(self, stmt):
		start_time = time.time()
		args = Validator.CreateTable(stmt, self._Integer, self._Char, self._Varchar)
		if not args:
			return self.__Result('Sintax error', start_time)
		
		table_name = args[0]
		fields = args[1:]
		# Creating pages
		if(self._CreateMetaPage(table_name, fields)):
			self._CreatePage(table_name, 0)
			return self.__Result('Table created', start_time)
		else:
			return self.__Result('Table already exists', start_time)

	def __InsertInto(self, stmt):
		args = Validator.InsertInto(stmt)
		if not args:
			return self.__Result('Sintax error', start_time)

		table_name = args[0]
		values = args[1:]
		if(not self._FileExists(table_name+'0', self._Group)):
			return self.__Result('Table not found', start_time, [])

		self._CreateFrame(table_name, 0, values)

	def __DeleteFrom(self, args): # recebe [2, tableName, [[attr, value],[attr, value]]]
		args = Validator.CreateTable(stmt)
		if not args:
			return self.__Result('Sintax error', start_time)

		offset = 0
		while(self._FileExists(table_name+str(offset), self._Group)):
			self._DeleteFrame(table_name, offset, args[1])
			offset += 1

	def __Select(self, args):
		args = Validator.CreateTable(stmt)
		if not args:
			return self.__Result('Sintax error', start_time)

		table_name = args[0]
		offset = 0
		values = []
		while(self._FileExists(table_name+str(offset), self._Group)):
			values = values + self._GetFrames(table_name,offset)
			offset += 1
		meta = self._GetMeta(table_name)
		aux = '\n| # | '
		for a in range(1, len(meta)):
			aux = aux + meta[a][2] + ' | '
		print(aux)
		for i in range(0,len(values)):
			aux = '| '+str(i+1)
			for j in range(0,len(values[i])):
				aux = aux +' | '+ str(values[i][j])
			print(aux+' |')
		return