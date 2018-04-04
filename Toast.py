# TOAST SECTION #

def CreateToastListPage(pageName, offset,LastUsedPage = 0):
	try:
		file = open('__pages__/'+pageName+str(offset)+'ToastList.dat', 'w+b')
		pageLen = 8*1024 # 8KB
		headerBytes = 8
		# criando o header
		pd_lower = headerBytes # Offset para começar o espaço livre
		ListLength = 0
		LastID = 0
		file.write(pd_lower.to_bytes(2,'little'))
		file.write(ListLength.to_bytes(2,'little'))
		file.write(LastUsedPage.to_bytes(2,'little'))
		file.write(LastID.to_bytes(2,'little'))
		# inicializando espaços vazios
		free = pageLen - headerBytes # bytes livres
		file.write(bytes(free))
		# salvando e fechando
		file.close()
		return True
	except IOError:
		print('Error creating '+pageName+str(offset)+'ToastList.dat')
		return False

def CreateToastPage(pageName, offset):
	try:
		file = open('__pages__/'+pageName+str(offset)+'Toast.dat', 'w+b')
		pageLen = 8*1024 # 8KB
		headerBytes = 2
		# criando o header
		pd_lower = headerBytes # Offset para começar o espaço livre
		file.write(pd_lower.to_bytes(2,'little'))
		# inicializando espaços vazios
		free = pageLen - headerBytes # bytes livres
		file.write(bytes(free))
		# salvando e fechando
		file.close()
		return True
	except IOError:
		print('Error creating '+pageName+str(offset)+'Toast.dat')
		return False

def CreateToastListFrame(pageName, offset, text):
	try:
		file = open('__pages__/'+pageName+str(offset)+'ToastList.dat', 'r+b')
		# calculando somatório de bytes da tupla e inserindo o nodo da lista e o nodo na pagina de toast
		file.seek(6,0)
		tupleLen = 12
		tupleId = int.from_bytes(file.read(4), 'little')
		tuplePointer = 0
		itemSize = len(text)

		file.seek(4,0) #posição do lastUsedPage
		lastUsedPage = int.from_bytes(file.read(2), 'little')

		file.seek(6,0)
		aux = tupleId + 1
		file.write(aux.to_bytes(4, 'little')) #atualizando o ultimo ID

		# verificando se há espaço na página
		file.seek(0, 0) # posição de início do pd_lower
		pd_lower = int.from_bytes(file.read(2), 'little') # lendo o ponteiro que indica onde colocar o próximo item

		if((8*1024 - pd_lower) < (tupleLen)): # se não há espaço
			file.close()
			CreateToastListPage(pageName, offset+1,lastUsedPage) # cria uma nova página
			return CreateToastListFrame(pageName, offset+1, text) # insere a tupla na nova página

		# gerenciando pd_lower
		file.seek(0, 0) # posição de início do pd_lower
		file.write((pd_lower+tupleLen).to_bytes(2, 'little')) # atualizando o ponteiro

		file.seek(4,0) #posição do lastUsedPage
		lastUsedPage = int.from_bytes(file.read(2), 'little')

		aux = CreateToastFrame(pageName,lastUsedPage,text) #retorna ponteiro do item e página
		tuplePointer = aux[0]
		LastUsedPage = aux[2]
		tuplePage = aux[1]

		file.seek(4,0) #atualizando o LUP
		file.write(LastUsedPage.to_bytes(2, 'little'))

		# criando o item
		file.seek(pd_lower, 0)
		file.write(tupleId.to_bytes(4, 'little'))
		file.write(tuplePage.to_bytes(2, 'little'))
		file.write(tuplePointer.to_bytes(2, 'little'))
		file.write(itemSize.to_bytes(4, 'little'))

		# atualizando tamanho da list	print(s)a de itens
		file.seek(2, 0) # posição de início do tlist
		tlist = 1 + int.from_bytes(file.read(2), byteorder='little') # tamanho atual da lista
		file.seek(2, 0) # posição de início do tlist
		file.write(tlist.to_bytes(2, 'little'))

		# salvando e fechando
		file.close()
		return tupleId
	except IOError:
		print('Error opening '+pageName+str(offset)+'ToastList.dat')
		return False

def CreateToastFrame(pageName,offset,text):
	try:
		file = open('__pages__/'+pageName+str(offset)+'Toast.dat', 'r+b')

		# verificando se há espaço na página
		file.seek(0, 0) # posição de início do pd_lower
		pd_lower = int.from_bytes(file.read(2), 'little') # lendo o ponteiro que indica onde colocar o próximo item
		tupleLen = len(text)
		if((pd_lower + tupleLen) <= (8*1024 - pd_lower)):
			# gerenciando pd_lower
			file.seek(0, 0) # posição de início do pd_lower
			file.write((pd_lower+tupleLen).to_bytes(2, 'little')) # atualizando o ponteiro
			file.seek(pd_lower,0)
			file.write(text.encode())
			aux = []
			aux.append(pd_lower)
			aux.append(offset)
			aux.append(offset)
			file.close()
			return aux

		remaining = 8*1024 - pd_lower
		if(remaining == 0):
			file.close() #salvando e fechando
			return CreateToastFrame(pageName, offset+1, text)
		insert = text[0:remaining]
		file.seek(pd_lower, 0) # posição de início do pd_lower
		file.write(insert.encode()) #inserindo o que dá
		file.seek(0,0) #atualizando pd_lower pro máximo
		file.write((8*1024).to_bytes(2, 'little'))

		CreateToastPage(pageName, offset+1) # cria uma nova página
		file.close() #salvando e fechando
		
		aux = []
		aux.append(pd_lower)
		aux.append(offset)
		aux.append(CreateToastFrame(pageName, offset+1, text[remaining:])[2])
		return aux
	except IOError:
		print('Error opening '+pageName+str(offset)+'Toast.dat')
		return False

def GetToastListFrame(id, pageName, offset = 0):
	file = open('__pages__/'+pageName+str(offset)+'ToastList.dat', 'r+b')

	file.seek(2,0)
	ListLength = int.from_bytes(file.read(2), byteorder='little')
	file.seek(8,0)
	for a in range(0,ListLength):
		aux = 8 + 12*a
		file.seek(aux,0)
		idAtual = int.from_bytes(file.read(4), byteorder='little')
		if(id == idAtual):
			page = int.from_bytes(file.read(2), byteorder='little')
			pointer = int.from_bytes(file.read(2), byteorder='little')
			size = 1+int.from_bytes(file.read(4), byteorder='little')
			file.close()
			return GetToastFrame(pageName,page,pointer,size)

	file.close()
	return GetToastListFrame(id, pageName, offset+1)


def GetToastFrame(pageName,offset,pointer,size,text = ''): #envie text como ''
	try:
		file = open('__pages__/'+pageName+str(offset)+'Toast.dat', 'r+b')

		file.seek(pointer, 0)

		if(size <= (8*1024 - pointer)):
			a = file.read(size).decode()
			file.close()
			return a

		remaining = size - (8*1024 - pointer)
		text = text + file.read(remaining).decode()
		size = size - remaining
		file.close() #salando e fechando
		return GetToastFrame(pageName,offset+1,2,size,text)
	except IOError:
		print('Error opening '+pageName+str(offset)+'Toast.dat')
		return False
