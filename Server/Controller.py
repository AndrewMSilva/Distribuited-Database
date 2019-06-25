import Validator
import Communicator
import Database
import sqlparse

class Controller(object):

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
		elif function == "SHOW":
			for i in range(0, len(stmt.tokens)):
				print(i, stmt.tokens[i])
			#ShowTable()
		else:
			print('aaa')

	def __CreateTable(self, stmt):
		args = Validator.CreateTable(stmt)
		Database.CreateTable(args)

	def __InsertInto(self, cmd):
		Database.InsertInto(cmd)

	def __DeleteFrom(self, cmd):
		Database.DeleteFrom(cmd)

	def __Select(self, cmd):
		Database.Select(cmd)

	def __ShowTable(self, cmd):
		Database.ShowTable(cmd)