# padrão de envio = [codigo do comando, nome da tabela, [valores de entrada (delete não precisa ser em lista)]]

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

def DeleteFrom(cmd):
	pass

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

# PAGES/FRAMES SECTION #

def PageExist(pageName, offset = ''):
	try:
		file = open('__pages__/'+pageName+str(offset)+'.dat', 'rb')
		file.close()
		return True
	except IOError:
		return False

def CreatePage(pageName, offset):
	try:
		file = open('__pages__/'+pageName+str(offset)+'.dat', 'w+b')
		pageLen = 8*1024 # 8KB
		special = 4 # bytes do frame especial
		headerBytes = 12
		# criando o header
		pd_tli = 0 # TLI da última mudança
		pd_lower = headerBytes # Offset para começar o espaço livre
		pd_upper = pageLen - special # Offset ao fim do espaço livre
		pd_special = pageLen - special # Deslocamento para o início do espaço especial
		pd_tlist = 0
		file.write(pd_tli.to_bytes(4,'big'))
		file.write(pd_lower.to_bytes(2,'little'))
		file.write(pd_upper.to_bytes(2,'little'))
		file.write(pd_special.to_bytes(2,'little'))
		file.write(pd_tlist.to_bytes(2,'little'))
		# inicializando espaços vazios
		free = pageLen - headerBytes - special # bytes livres
		file.write(bytes(free))
		# alocando frame especial
		file.write(bytes(special))
		# salvando e fechando
		file.close()
		return True
	except IOError:
		print('Error creating '+pageName+str(offset)+'.dat')
		return False

def CreateFrame(pageName, offset, values): # n = o somatório dos bytes da tupla
	try:
		file = open('__pages__/'+pageName+str(offset)+'.dat', 'r+b')
		# calculando somatório de bytes da tupla e verificando os tipos
		tupleLen = 0
		meta = GetMeta(pageName)
		metaLen = meta[0]
		meta = meta[1:]
		for i in range(0,metaLen):
			if(meta[i][0] == 1 and isinstance(values[i], int)): # se ambos int
				tupleLen += meta[i][1]
			elif(meta[i][0] == 2 and isinstance(values[i], str)): # se char e str
				tupleLen += meta[i][1]
			elif(meta[i][0] == 3 and isinstance(values[i], str)): # se varchar e str
				tupleLen += len(values[i])
			else:
				print('Entry and type do not match: check the sequence') # a entrada e o tipo não combinam
				file.close()
				return False
		# verificando se há espaço na página
		file.seek(4, 0) # posição de início do pd_lower
		pd_lower = int.from_bytes(file.read(2), 'little') # lendo o ponteiro que indica onde colocar o próximo item
		file.seek(6, 0) # posição de início do pd_upper
		pd_upper = int.from_bytes(file.read(2), 'little') # lendo o ponteiro que indica onde colocar a próxima tupla
		itemLen = 3 + 2*len(values)

		if((pd_upper - pd_lower) < (tupleLen + itemLen)): # se não há espaço
			file.close()
			if(PageExist(pageName, offset+1)): # se existe uma página seguinte
				CreateFrame(pageName, offset+1, values) # tenta inserir na próxima página
			else: # se não existe uma págica seguinte
				CreatePage(pageName, offset+1) # cria uma nova página
				CreateFrame(pageName, offset+1, values) # insere a tupla na nova página
			return True
		# gerenciando pd_lower
		file.seek(4, 0) # posição de início do pd_lower
		file.write((pd_lower+itemLen).to_bytes(2, 'little')) # atualizando o ponteiro

        # gerenciando pd_upper
		file.seek(6, 0) # posição de início do pd_upper
		file.write((pd_upper-tupleLen-1).to_bytes(2, 'little')) # atualizando o ponteiro

		# criando o item
		file.seek(pd_lower, 0)
		pointer = pd_upper-tupleLen-1 # ponteiro para a tupla
		status = 1 # estado da tupla (1=sendo usado, 0=livre)
		file.write(pointer.to_bytes(2, 'little'))
		file.write(status.to_bytes(1, 'little'))
		for i in range(0,len(meta)):
			if(meta[i][0] == 1): # se for int
				file.write(meta[i][1].to_bytes(2, 'little'))
			else: # se não for seguinte
				file.write(len(values[i]).to_bytes(2, 'little'))

		# criando a tupla
		file.seek(pointer, 0)
		for i in range(0,len(meta)):
			if(meta[i][0] == 1): # se for int
				file.write(values[i].to_bytes(4, 'little'))
			elif(meta[i][0] == 2): # se for char
				b = len(values[i])
				for a in range(b,meta[i][1]):
					values[i] += "0"
				file.write(values[i].encode())
				# file.seek() # NÃO SEI BEM COMO FAREMOS PRA DAR O ESPAÇO RESTANTE DO CHAR E SABER IGORAR ELE QUANDO PEGAR O VALOR
			else: # se for varchar
				file.write(values[i].encode())

		# atualizando tamanho da list	print(s)a de itens
		file.seek(10, 0) # posição de início do tlist
		tlist = 1 + int.from_bytes(file.read(2), byteorder='little') # tamanho atual da lista
		file.seek(10, 0) # posição de início do tlist
		file.write(tlist.to_bytes(2, 'little'))

		# salvando e fechando
		file.close()
		return True
	except IOError:
		print('Error opening '+pageName+str(offset)+'.dat')
		return False


def CreateMetaPage(pageName,attr): # [[type,typeLen,nameLen,name],...] | cria a página com os campos da tupla
	try:
		file = open('__pages__/'+pageName+'meta.dat', 'wb')
		# pega os atributos já verificados e insere um por vez
		pageLen = 8*1024 # 8KB
		metaLen = len(attr)
		file.write(metaLen.to_bytes(1,'little')) # quantidade de atributos do meta
		for a in attr:
			file.write(a[0].to_bytes(1,'little')) #tipo do campo
			file.write(a[1].to_bytes(1,'little')) #tamanho do campo
			file.write(a[2].to_bytes(1,'little')) #tamanho do nome
			file.write(a[3].encode()) #pra string
		file.write(bytes(pageLen - metaLen))
		# salvando e fechando
		file.close()
		return True
	except IOError:
		print('Error creating '+pageName+'meta.dat') #não deu pra criar a página
		return False

def GetMeta(pageName): #pegar os atributos da tabela
	try:
		file = open('__pages__/'+pageName+'meta.dat', 'rb')
		attr = []
		metaLen = int.from_bytes(file.read(1), byteorder='little') # tamanho do meta
		attr.append(metaLen)
		for i in range(0, metaLen):
			v = []
			a = int.from_bytes(file.read(1), byteorder='little') #tipo do primeiro campo, se não existir retorna um vetor vazio
			v.append(a)
			a = int.from_bytes(file.read(1), byteorder='little') #tamanho do campo
			v.append(a)
			a = int.from_bytes(file.read(1), byteorder='little')#tamanho do nome do campo
			a = file.read(a).decode()
			v.append(a)
			attr.append(v)
		file.close()
		return attr
	except IOError:
		print('Error opening '+pageName+'meta.dat') #página não existe
		return False

def GetFrames(pageName,offset):
	try:
		file = open('__pages__/'+pageName+str(offset)+'.dat', 'rb')
		data = []
		meta = GetMeta(pageName)
		metaLen = int(meta[0])
		meta = meta[1:]
		itemLen = 3 + 2*metaLen
		file.seek(10,0)
		tlist = int.from_bytes(file.read(10),byteorder='little')
		file.seek(4,0)
		lower = int.from_bytes(file.read(2),byteorder='little')
		for itemP in range(12, lower, itemLen):
			file.seek(itemP, 0)
			aux = []
			pointer = int.from_bytes(file.read(2), byteorder='little') #ponteiro pra tupla
			status = int.from_bytes(file.read(1), byteorder='little') #status
			if(status == 0): # vai para o próximo item se este não estiver sendo usado
				continue
			attrLen = []
			# pegando os tamanhos dos campos
			for i in range(0, metaLen):
				attrLen.append(int.from_bytes(file.read(2), byteorder='little'))
			# pegando a tupla
			file.seek(pointer, 0)
			for i in range(0, metaLen):
				if(meta[i][0] == 1): #lendo int
					aux.append(int.from_bytes(file.read(attrLen[i]), byteorder='little')) #tamanho do campo
				elif(meta[i][0] == 2): # char
					aux.append(file.read(attrLen[i]+1).decode())
					file.seek(file.tell()+meta[i][1]-attrLen[i], 0)
				else: #char e varchar PRECISA DO TOAST NISSO DPS
					aux.append(file.read(attrLen[i]).decode())
			data.append(aux)
		data = list(reversed(data))
		return data
	except IOError:
		print('Error opening '+pageName+str(offset)+'.dat') #página não existe
		return False
