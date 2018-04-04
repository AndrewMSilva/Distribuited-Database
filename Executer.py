import PageManager

def Read(cmd):
    if(cmd[0] == 0):
    	CreateTable(cmd[1:])
    elif(cmd[0] == 1):
    	InsertInto(cmd[1:])
    elif(cmd[0] == 2):
    	DeleteFrom(cmd[1:])
    elif(cmd[0] == 3):
    	Select(cmd[1:])
    elif(cmd[0] == 4):
    	ShowTable(cmd[1:])

def CreateTable(cmd):
	if(PageExist(cmd[0]+'meta')): #se já existe n cria denovo e retorna nada
		print("Table already exists: "+cmd[0])
		return
	values = []
	for a in cmd[1:]: #pega os atributos do comando
		v = []
		if(a[1] == 'int'): #caso o atributo seja inteiro
			v.append(1)
			v.append(4) #tamanho fixo, mas será desconsiderado
			v.append(len(a[0])) #tamanho do nome do campo
			v.append(a[0]) #nome do campo
		elif(a[1][0:4] == 'char'): #caso seja char
			v.append(2)
			v.append(int((a[1].split('(')[1].split(')'))[0])) #tamanho do char
			v.append(len(a[0]))#tamanho do nome do campo
			v.append(a[0])#nome do campo
		else: #caso seja varchar
			v.append(3)
			v.append(int((a[1].split('(')[1].split(')'))[0])) #tamanho do char
			v.append(len(a[0])) #tamanho do nome do campo
			v.append(a[0]) #nome do campo
		values.append(v)
	CreateMetaPage(cmd[0],values)
	CreatePage(cmd[0],0)

def InsertInto(cmd):
	if(not PageExist(cmd[0], 0)): #se já existe n cria denovo e retorna nada
		print("Table not found: "+cmd[0])
		return

	for values in cmd[1:]:
		CreateFrame(cmd[0], 0, values)

def DeleteFrom(cmd): # recebe [2, tableName, [[attr, value],[attr, value]]]
	offset = 0
	while(PageExist(cmd[0],offset)):
		DeleteFrame(cmd[0], offset, cmd[1])
		offset += 1

def Select(cmd):
	offset = 0
	values = []
	while(PageExist(cmd[0],offset)):
		values = values + GetFrames(cmd[0],offset)
		offset += 1
	print(values)
	return

def ShowTable(cmd):
	meta = GetMeta(cmd[0])
	print(cmd[0]+' attributes:')
	for a in meta[1:]:
		s = a[2]+' '
		if(a[0] == 1):
			s += 'int'
		elif(a[0] == 2):
			s += 'char('+str(a[1])+')'
		elif(a[0] == 3):
			s += 'varchar('+str(a[1])+')'
		print(s)
