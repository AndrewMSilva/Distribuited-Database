# padrão de envio = [codigo do comando, nome da tabela, [valores de entrada (delete não precisa ser em lista)]]

def Read(cmd):
    if(cmd[0] == 0):
    	CreateTable(cmd[1:])
    if(cmd[0] == 1):
    	InsertInto(cmd[1:])
    if(cmd[0] == 2):
    	DeleteFrom(cmd[1:])

def MetadataPage():
	try:
		file = open('__pages__/metadata.dat', 'rb')
		file.close()
		return True
	except IOError:
		if(CreatePage('metadata')):
			return True
		else:
			return False

def CreateTable(cmd):
	if(not MetadataPage()):
		return
	CreatePage(cmd[0])
	values = []
	for a in cmd[1:]:
		values.append(a[0])
		values.append(a[1])
	CreateFrame('metadata', values)

def InsertInto(cmd):
	CreateFrame(cmd[0], cmd[1:])

def DeleteFrom(cmd):
	pass

def List(cmd, pageName):
	with open('page0.dat', 'rb') as file:
	    byte = file.read(1)
	    while byte != b'':
	        print(byte)
	        byte = file.read(1)

# PAGES/FRAMES SECTION #

def CreatePage(pageName):
	try:
		file = open('__pages__/'+pageName+'.dat', 'wb')
		pageLen = 8*1024 # 8KB
		special = 4 # bytes do frame especial
		# criando o header
		pd_lsn = pageLen - special - 1 # LSN: próximo byte após o último byte do registro xlog para a última alteração nesta página
		pd_tli = 0 # TLI da última mudança
		pd_lower = pageLen - special - 1 # Offset para começar o espaço livre
		pd_upper = 20 # Offset ao fim do espaço livre
		pd_special = pageLen - special # Deslocamento para o início do espaço especial
		pd_pagesize_version = 8 # Tamanho da página
		file.write(pd_lsn.to_bytes(8,'big'))
		file.write(pd_tli.to_bytes(4,'big'))
		file.write(pd_lower.to_bytes(2,'little'))
		file.write(pd_upper.to_bytes(2,'little'))
		file.write(pd_special.to_bytes(2,'little'))
		file.write(pd_pagesize_version.to_bytes(2,'little'))
		# inicializando espaços vazios
		free = pageLen - 20 - special # bytes livres
		file.write(bytes(free))
		# alocando frame especial
		file.write(bytes(special))
		# salvando e fechando
		file.close()
		return True
	except IOError:
		print('Error creating '+pageName+'.dat')
		return False

def CreateFrame(pageName, values):
	try:
		file = open('__pages__/'+pageName+'.dat', 'r+b')
		# calculando somatório de bytes
		n = 0
		for a in values:
			if(isinstance(a, str)):
				n += len(a)
			else:
				n += 4
		# gerenciando pd_upper
		file.seek(16) # posição de início do pd_upper
		i = int.from_bytes(file.read(2), 'little') # lendo o ponteiro que indica onde colocar o próximo item
		file.seek(16) # posição de início do pd_upper
		file.write(int(i+4).to_bytes(2, 'little')) # atualizando o ponteiro
		# criando o item
		file.seek(i)
		file.write(n.to_bytes(4,'little'))

		# gerenciando pd_lower
		file.seek(18) # posição de início do pd_lower
		i = int.from_bytes(file.read(2), 'little') # lendo o ponteiro que indica onde colocar a próxima tupla
		file.seek(18) # posição de início do pd_lower
		file.write((i+4).to_bytes(2, 'little')) # atualizando o ponteiro
		# criando a tupla
		file.seek(i)
		for a in values:
			if(isinstance(a, str)):
				file.write(a.encode())
			else:
				file.write(a.to_bytes(4, 'litte'))

		# salvando e fechando
		file.close()
		return True
	except IOError:
		print('Error opening '+pageName+'.dat')
		return False


class Table: # classe apenas experimental
	attr = []	# [[name,numBytes]]
	PK = None	# attr[PK] == PK (usável se for usar árvore binária para os índices)

	def __init__(self, cmd):
		self.name = cmd[0]
		for i in range(1,len(cmd)):
			self.attr.append([cmd[i][1]]) # nome
			if(cmd[i][0] == 'int'):
				self.attr[i-1].append(4) # bytes do int
			else:
				a = cmd[i][0].split('(')
				self.attr[i-1].append(int(a[1][0:(len(a[1])-1)])) # bytes do char/varchar (o número entre parênteses)
