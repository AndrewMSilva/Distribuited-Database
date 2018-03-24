# padrão de envio = [codigo do comando, nome da tabela, [valores de entrada (delete não precisa ser em lista)]]

def Read(cmd):
    if(cmd[0] == 0):
    	CreateTable(cmd[1:])
    if(cmd[0] == 1):
    	InsertInto(cmd[1:])
    if(cmd[0] == 2):
    	DeleteFrom(cmd[1:])
    if(cmd[0] == 3):
    	Select(cmd[1:])

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
			v.append(len(a[1])) #tamanho do nome do campo
			v.append(a[1]) #nome do campo
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
    s = []
    while(PageExist(cmd[0],offset)):
        s = s + GetFrames(cmd[0],offset)
        offset += 1
    print(s)
    return

def List(cmd, pageName):
	with open('page0.dat', 'rb') as file:
	    byte = file.read(1)
	    while byte != b'':
	        print(byte)
	        byte = file.read(1)

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
		pd_upper = pageLen - special - 1 # Offset ao fim do espaço livre
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
		for i in range(0,len(meta)):
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
		print(tupleLen)
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
		file.write((pd_upper-tupleLen).to_bytes(2, 'little')) # atualizando o ponteiro

		# criando o item
		file.seek(pd_lower, 0)
		pointer = pd_upper-tupleLen # ponteiro para a tupla
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
				print("batata é" + values[i])
				file.write(values[i].encode())
				# file.seek() # NÃO SEI BEM COMO FAREMOS PRA DAR O ESPAÇO RESTANTE DO CHAR E SABER IGORAR ELE QUANDO PEGAR O VALOR
			else: # se for varchar
				file.write(values[i].encode())

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
		attr = []
		meta = GetMeta(pageName)
		meta = meta[0]
		file.seek(4,0)
		low = int.from_bytes(file.read(2),byteorder='little')
		file.seek(12,0)
		print(low)
		exit()
		while(file.tell() < low):
			for i in range(0,low/(3+(2*meta))):
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
