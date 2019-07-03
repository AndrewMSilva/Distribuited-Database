from pyparsing import *

def CreateTable(stmt, integer, char, varchar):
	if not stmt.has_alias():
		None
	table_name = None
	expected = 'CREATE'
	for token in stmt.tokens:
		if token.value == " ":
			continue
		elif not expected:
			break
		elif expected == 'table':
			table_name = token.value
			expected = None
		elif token.value == expected:
			if expected == 'CREATE':
				expected = 'TABLE'
			elif expected == 'TABLE':
				expected = 'table'

	if expected or not table_name:
		return None

	args = [table_name]
	attr = token.value
	if attr[0] == "(" and attr[-1] == ")":
		attr = attr[1:len(attr)-1]
		if "," in attr:
			attr = attr.split(",")
		else:
			attr = [attr]
		for i in range(0, len(attr)):
			attr[i] = attr[i].split()
			field = []
			if len(attr[i]) == 2:
				length = 4 # integer length (in bytes)
				if attr[i][1] == 'integer':
					field.append(integer)
					field.append(length) 	      # integer length (in bytes)
					field.append(len(attr[i][0])) # field name length
					field.append(attr[i][0]) 	  # field name
				elif attr[i][1][0:4] == 'char':
					field.append(char)
					length = int((attr[i][1].split('(')[1].split(')'))[0])
					field.append(length) 	      # char length (in bytes)
					field.append(len(attr[i][0])) # field name length
					field.append(attr[i][0]) 	  # field name
				elif attr[i][1][0:7] == 'varchar':
					field.append(varchar)
					length = int((attr[i][1].split('(')[1].split(')'))[0])
					field.append(length) 	      # varchar length in bytes
					field.append(len(attr[i][0])) # field name length
					field.append(attr[i][0]) 	  # field name
				else:
					return None
				if length < 0:
					return None
			else:
				return None
			args.append(field)
	else:
		return None

	return args

def InsertInto(stmt):
	if not stmt.has_alias():
		None
	table_name = None
	expected = 'INSERT'
	for token in stmt.tokens:
		if token.value == " ":
			continue
		elif not expected and 'VALUES' in token.value:
			break
		elif expected == 'table':
			table_name = token.value
			expected = None
		elif token.value == expected:
			if expected == 'INSERT':
				expected = 'INTO'
			elif expected == 'INTO':
				expected = 'table'
	
	if expected or not table_name:
		return None

	args = [table_name]
	attr = token.value
	if 'VALUES' in attr:
		attr = attr.replace('VALUES', '')
		try:
			value = eval(attr)
			if isinstance(value, tuple):
				args += list(value)
			else:
				args += [value]
			return args
		except:
			return None
	else:
		return None