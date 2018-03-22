# padrão de envio = [codigo do comando, nome da tabela, [valores de entrada (delete não precisa ser em lista)]]

def Read(cmd):
    if(cmd[0] == 0):
    	CreateTable(cmd[1:])
    if(cmd[0] == 1):
    	InsertInto(cmd[1:])
    if(cmd[0] == 2):
    	DeleteFrom(cmd[1:])

def MetaPage(pageName): #verifica se a página já existe
	try:
		file = open('__pages__/'+pageName+'meta.dat', 'rb')
		file.close()
		return False
	except IOError:
		return True

def CreateTable(cmd):
	if(not MetaPage(cmd[0])): #se já existe n cria denovo e retorna nada
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
		elif(a[1:4] == 'char'): #caso seja char
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
	if(MetaPage(cmd[0])): #se já existe n cria denovo e retorna nada
		print("Table not found: "+cmd[0])
		return
	# AQUI TEMOS QUE VERIFICAR AS PÁGINAS COM ESPAÇO PRA INSERIR A TUPLA
	# EU "CALCULO" O TAMNHO DA TUPLA DENTRO DA FUNÇÃO, ENTÃO TERÍAMOS QUE 
	# CALCULAR AQUI E MANDAR PRO PARÂMETRO

	#i = 0
	#while():
	#	if(PageExist(cmd[0], i)):

	CreateFrame(cmd[0], 0, cmd[1:])

def DeleteFrom(cmd):
	pass

def List(cmd, pageName):
	with open('page0.dat', 'rb') as file:
	    byte = file.read(1)
	    while byte != b'':
	        print(byte)
	        byte = file.read(1)

# PAGES/FRAMES SECTION #

def PageExist(pageName, offset):
	try:
		file = open('__pages__/'+pageName+str(offset)+'.dat', 'rb')
		file.close()
		return True
	except IOError:
		return False

def CreatePage(pageName, offset):
	try:
		file = open('__pages__/'+pageName+str(offset)+'.dat', 'wb')
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

def CreateFrame(pageName, offset, values):
	try:
		file = open('__pages__/'+pageName+str(offset)+'.dat', 'r+b')
		# calculando somatório de bytes
		n = 0
		meta = GetMeta(pageName)
		for i in range(0,len(meta)):
			if(meta[i][0] == 1 and isinstance(values[0][i], int)):
				n += meta[i][1]
			elif(meta[i][0] == 2 and isinstance(values[0][i], str)):
				n += meta[i][1]
			elif(meta[i][0] == 3 and isinstance(values[0][i], str)):
				n += len(values[0][i])
			else:
				print('Invalid insertion string')
				return
		# --------------------------------
		# CONFIGURAR O RID E OS PONTEIROS E SOMAR NO N
		# --------------------------------
		# gerenciando pd_lower
		file.seek(6) # posição de início do pd_lower
		i = int.from_bytes(file.read(2), 'little') # lendo o ponteiro que indica onde colocar o próximo item
		file.seek(6) # posição de início do pd_lower
		file.write(int(i+4).to_bytes(2, 'little')) # atualizando o ponteiro
		# criando o item
		file.seek(i)
		file.write(n.to_bytes(4,'little'))

		# gerenciando pd_upper
		file.seek(8) # posição de início do pd_upper
		i = int.from_bytes(file.read(2), 'little') # lendo o ponteiro que indica onde colocar a próxima tupla
		file.seek(8) # posição de início do pd_upper
		file.write((i-n).to_bytes(2, 'little')) # atualizando o ponteiro
		# criando a tupla
		# --------------------------------
		# CRIAR O RID E OS PONTEIROS
		# --------------------------------
		file.seek(i)
		for j in range(0,len(meta)):
			if(meta[j][0] == 1): # se for int
				file.write(values[0][j].to_bytes(4, 'little'))
			elif(meta[j][0] == 2): # se for char
				file.write(values[0][j].encode())
				# file.seek() # NÃO SEI BEM COMO FAREMOS PRA DAR O ESPAÇO RESTANTE DO CHAR E SABER IGORAR ELE QUANDO PEGAR O VALOR
			else:
				file.write(values[0][j].encode())

		# salvando e fechando
		file.close()
		return True
	except IOError:
		print('Error opening '+pageName+'.dat')
		return False


def CreateMetaPage(pageName,attr): # [[type,typeLen,nameLen,name],...] | cria a página com os campos da tupla
	try:
		file = open('__pages__/'+pageName+'meta.dat', 'wb')
		# pega os atributos já verificados e insere um por vez
		for a in attr:
			file.write(a[0].to_bytes(1,'little')) #tipo do campo
			file.write(a[1].to_bytes(1,'little')) #tamanho do campo
			file.write(a[2].to_bytes(1,'little')) #tamanho do nome
			file.write(a[3].encode()) #pra string
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
		a = int.from_bytes(file.read(1), byteorder='little') #tipo do primeiro campo, se não existir retorna um vetor vazio
		while(a):
			v = []			
			v.append(a)
			a = int.from_bytes(file.read(1), byteorder='little') #tamanho do campo
			v.append(a)
			a = int.from_bytes(file.read(1), byteorder='little')#tamanho do nome do campo
			a = file.read(a).decode()
			v.append(a)
			attr.append(v)
			a = int.from_bytes(file.read(1), byteorder='little') #nome do campo
		file.close()
		return attr
	except IOError:
		print('Error opening '+pageName+'meta.dat') #página não existe
		return False