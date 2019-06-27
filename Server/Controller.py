from Service import Service
from PageManager import PageManager
import Validator
import sqlparse

class Controller(Service, PageManager):

	def _HandleMessage(self, message):
		print(message)

	def Execute(self, query):
		query = sqlparse.format(query, reindent=True, keyword_case="upper")
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
			print('aaa')
	
	def __CreateTable(self, stmt):
		args = Validator.CreateTable(stmt, self._Integer, self._Char, self._Varchar)
		table_name = args[0]
		fields = args[1:]
		# Check if the table already exists
		if(self._PageExist(table_name+self._MetaData)):
			print("Table already exists: "+table_name)
			return
		# Creating table files
		self._CreateMetaPage(table_name, fields)
		self._CreatePage(table_name, 0)
		self._CreateToastPage(table_name, 0)
		self._CreateToastControllerPage(table_name, 0)

	def __InsertInto(self, stmt):
		args = Validator.InsertInto(stmt)
		table_name = args[0]
		values = args[1:]

		if(not self._PageExist(table_name, 0)): #se já existe n cria denovo e retorna nada
			print("Table not found: "+table_name)
			return

		self._CreateFrame(table_name, 0, values)

	def __DeleteFrom(self, args): # recebe [2, tableName, [[attr, value],[attr, value]]]
		args = Validator.CreateTable(stmt)

		offset = 0
		while(self._PageExist(table_name,offset)):
			self._DeleteFrame(table_name, offset, args[1])
			offset += 1

	def __Select(self, args):
		args = Validator.CreateTable(stmt)
		table_name = args[0]

		offset = 0
		values = []
		while(self._PageExist(table_name,offset)):
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