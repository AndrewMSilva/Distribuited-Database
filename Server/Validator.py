def CreateTable(stmt):
	if not stmt.has_alias():
		None
	table_name = stmt.get_alias()
	expected = "CREATE"
	for token in stmt.tokens:
		if token.value == " ":
			continue
		elif not expected:
			break
		elif token.value == expected:
			if expected == "CREATE":
				expected = "TABLE"
			elif expected == "TABLE":
				expected = table_name
			elif expected == table_name:
				expected = None
	
	if expected:
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
			if(len(attr[i]) != 2 or (attr[i][1] != 'int' and attr[i][1][0:4] != 'char' and attr[i][1][0:7] != 'varchar')):
				return None
			args.append(attr[i])
	else:
		return None

	return args
	
	"""


def InsertInto(cmd):
	try:
		# Definindo tipos aceitos
		object_name = Regex('[a-zA-Z_]+')
		number = Regex('-?[0-9]+')
		string = QuotedString("'") | QuotedString('"')
		term = number | string # número ou string
		# Definindo expressões regulares
		term_list = (delimitedList(term)).setResultsName('terms')
		table_name = object_name.setResultsName('table')
		# Validando SQL
		sql_stmt = "insert into " + table_name + "(" + term_list + ")"
		res = sql_stmt.parseString(cmd)
		query = [Function.InsertInto, res.table, list(res.terms)]
		for i in range(0, len(query[2])):
			try:
				query[2][i] = int(query[2][i])
			except ValueError:
				continue
		return query
	except ParseException as pe:
		return False

def DeleteFrom(cmd):
	if(cmd[0] != ' '):
		return False
	i = 1
	status = -1
	attr = [Function.DeleteFrom, False]
	values = []
	for j in range(i,len(cmd)):
		if(status == -1 and cmd[j] != ' '): # procurando onde começa o nome da tabela
			status = 0
			i = j
		elif(status == 0 and cmd[j-5:j] == 'where'): # procurando o 'where'
			attr[1] = cmd[i:j-6]
			attr[1] = attr[1].split(' ')[0]
			status = 1
		elif(status == 1 and (cmd[j] != ' ')): # procurando onde começa os argumentos
			s = cmd[j:].split(',');
			for a in s:
				v = a.split('=')
				v[0] = v[0].split(' ')[0]
				if(v[1].find("'") == -1):
					v[1] = int(v[1])
				else:
					v[1] = v[1].cmd[i].split("'")[0]
				values.append(v)
			attr.append(values)
			break
	if(not attr[0]):
		return False
	return attr

def Select(cmd):
	if(cmd[0] != ' '):
		return False
	i = 1
	attr = [Function.Select, False]
	status = 0
	for j in range(i,len(cmd)):
		if(status == 0 and cmd[j] != ' '): # procurando onde começam os campos
			i = j
			status = 1
		elif(status == 1 and cmd[j-4:j] == 'from'): #procurando o 'from'
			c = cmd[i:j-5]
			c = c.split(',')
			for i in range(0,len(c)):
				c[i] = c[i].replace(" ", "") # removendo espaços
			attr.append(c)
			status = 2
		elif(status == 2 and cmd[j] != ' '): # procurando onde começa o nome da tabela
			status = 3
			i = j
		elif(status == 3 and (cmd[j] == ' ' or (j+1) == len(cmd))): # procurando onde termina o nome da tabela
			attr[1] = cmd[i:j+1]
			attr[1] = attr[1].split(' ')[0]
			status = 4
	if(not attr[0]):
		return False
	return attr # [3, tableName, [campos...]]

def ShowTable(cmd):
	if(cmd[0] != ' '):
		return False
	i = 1
	status = 0
	attr = [Function.ShowTable, False]
	for j in range(i,len(cmd)):
		if(status == 0 and cmd[j] != ' '): # procurando onde começa o nome da tabela
			status = 1
			i = j
		elif(status == 1 and (cmd[j] == ' ' or (j+1) == len(cmd))): # procurando onde termina o nome da tabela
			attr[1] = cmd[i:j+1]
			attr[1] = attr[1].split(' ')[0]
	if(not attr[0]):
		return False
	return attr"""
