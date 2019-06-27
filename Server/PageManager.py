
class PageManager(object):
	# Files settings
	_Directory = './Pages/'
	_MetaData  = 'Meta'
	_Extension = '.page'
	_Length    = 8*1024
	# Toast settings
	_ToastContent    = 'Toast'
	_ToastController = 'ToastList'
	# Variable types
	_Integer = 0
	_Char 	 = 1
	_Varchar = 2
	_Toast   = 3
	# Values settings
	_MaxStringLen = 255

	# PAGES SECTION #
	def _PageExist(self, pageName, offset = ''):
		try:
			file = open(self._Directory+pageName+str(offset)+self._Extension, 'rb')
			file.close()
			return True
		except IOError:
			return False

	def _CreatePage(self, pageName, offset):
		try:
			file = open(self._Directory+pageName+str(offset)+self._Extension, 'w+b')
			special = 0 # bytes do frame especial
			headerBytes = 12
			# criando o header
			pd_tli = 0 # TLI da última mudança
			pd_lower = headerBytes # Offset para começar o espaço livre
			pd_upper = self._Length - special # Offset ao fim do espaço livre
			pd_special = self._Length - special # Deslocamento para o início do espaço especial
			pd_tlist = 0
			file.write(pd_tli.to_bytes(4,'little'))
			file.write(pd_lower.to_bytes(2,'little'))
			file.write(pd_upper.to_bytes(2,'little'))
			file.write(pd_special.to_bytes(2,'little'))
			file.write(pd_tlist.to_bytes(2,'little'))
			# inicializando espaços vazios
			free = self._Length - headerBytes - special # bytes livres
			file.write(bytes(free))
			# alocando frame especial
			file.write(bytes(special))
			# salvando e fechando
			file.close()
			return True
		except IOError:
			print('Error creating '+pageName+str(offset)+self._Extension)
			return False

	def _CreateFrame(self, pageName, offset, values): # n = o somatório dos bytes da tupla
		try:
			file = open(self._Directory+pageName+str(offset)+self._Extension, 'r+b')
			# calculando somatório de bytes da tupla e verificando os tipos
			tupleLen = 0
			meta = self._GetMeta(pageName)
			metaLen = meta[0]
			meta = meta[1:]
			if(metaLen != len(values)):
				print('Table '+pageName+' have '+str(metaLen)+' attributes')
				file.close()
				return False
			for i in range(0,metaLen):
				if(meta[i][0] == self._Integer and isinstance(values[i], int)): # se ambos int
					tupleLen += meta[i][1]
				elif(meta[i][0] == self._Char and isinstance(values[i], str)): # se char e str
					if(meta[i][1] > self._MaxStringLen):
						tupleLen += 4
					elif(len(values[i]) <= meta[i][1]):
						tupleLen += meta[i][1]
					else:
						print('The attribute is char('+str(meta[i][1])+'), but has received '+str(len(values[i]))+' characteres') # a entrada e o tipo não combinam
						file.close()
						return False
				elif(meta[i][0] == self._Varchar and isinstance(values[i], str)): # se varchar e str
					if(len(values[i]) > self._MaxStringLen):
						tupleLen += 4
					elif(len(values[i]) <= meta[i][1]):
						tupleLen += len(values[i])
					else:
						print('The attribute is varchar('+str(meta[i][1])+'), but has received '+str(len(values[i]))+' characteres') # a entrada e o tipo não combinam
						file.close()
						return False
				else:
					print('Entry and type do not match: check the sequence') # a entrada e o tipo não combinam
					file.close()
					return False
			# verificando se há espaço na página
			file.seek(4, 0) # posição de início do pd_lower
			pd_lower = int.from_bytes(file.read(2), 'little') # lendo o ponteiro que indica onde colocar o próximo item
			file.seek(6, 0) # posição de início do pd_upper
			pd_upper = int.from_bytes(file.read(2), 'little') # lendo o ponteiro que indica onde colocar a próxima tupla
			itemLen = 3 + 3*len(values)

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
				if(meta[i][0] == self._Integer): # se for int
					file.write(meta[i][0].to_bytes(1, 'little'))
					file.write(meta[i][1].to_bytes(2, 'little'))
				elif(meta[i][0] == self._Char): # se for char
					if(meta[i][1] > self._MaxStringLen):
						meta[i][0] = 4
					file.write(meta[i][0].to_bytes(1, 'little'))
					file.write(len(values[i]).to_bytes(2, 'little'))
				else: # se for varchar ou toast
					if(len(values[i]) > self._MaxStringLen):
						meta[i][0] = self._Toast
					file.write(meta[i][0].to_bytes(1, 'little'))
					file.write(len(values[i]).to_bytes(2, 'little'))

			# criando a tupla
			file.seek(pointer, 0)
			for i in range(0,len(meta)):
				if(meta[i][0] == self._Integer): # se for int
					file.write(values[i].to_bytes(4, 'little'))
				elif(meta[i][0] == self._Char): # se for char
					b = len(values[i])
					for a in range(b,meta[i][1]):
						values[i] += "0"
					file.write(values[i].encode())
				elif(meta[i][0] == self._Varchar): # se for varchar
					file.write(values[i].encode())
				elif(meta[i][0] == self._Toast):
					aux = CreateToastControllerFrame(pageName,0,values[i])
					file.write(aux.to_bytes(4,'little'))
			# atualizando tamanho da list	print(s)a de itens
			file.seek(10, 0) # posição de início do tlist
			tlist = 1 + int.from_bytes(file.read(2), byteorder='little') # tamanho atual da lista
			file.seek(10, 0) # posição de início do tlist
			file.write(tlist.to_bytes(2, 'little'))

			# salvando e fechando
			file.close()
			return True
		except IOError:
			print('Error opening '+pageName+str(offset)+self._Extension)
			return False

	def _DeleteFrame(self, pageName, offset, values):
		try:
			file = open(self._Directory+pageName+str(offset)+self._Extension, 'r+b')
			meta = self._GetMeta(pageName)
			metaLen = meta[0]
			meta = meta[1:]
			# procurando e deletando registros
			itemLen = 3 + 3*metaLen
			file.seek(4,0)
			lower = int.from_bytes(file.read(2),byteorder='little')
			for itemP in range(12, lower, itemLen):
				file.seek(itemP, 0)
				pointer = int.from_bytes(file.read(2), byteorder='little') #ponteiro pra tupla
				status = int.from_bytes(file.read(1), byteorder='little') #status
				if(status == 0): # vai para o próximo item se este não estiver sendo usado
					continue
				attrLen = []
				attrType = []
				# pegando os tamanhos dos campos
				for i in range(0, metaLen):
					attrType.append(int.from_bytes(file.read(1), byteorder='little'))
					attrLen.append(int.from_bytes(file.read(2), byteorder='little'))
				# pegando a tupla
				file.seek(pointer, 0)
				for i in range(0, metaLen):
					encontrou = False
					v = 0
					if(attrType[i] == self._Integer): #lendo int
						v = int.from_bytes(file.read(attrLen[i]), byteorder='little') #tamanho do campo
					elif(attrType[i] == self._Char): # char
						v = file.read(attrLen[i]+1).decode()
						file.seek(file.tell()+meta[i][1]-attrLen[i], 0)
					elif(attrType[i] == self._Varchar): # varchar
						v = file.read(attrLen[i]).decode()
					elif(attrType[i] == self._Toast): # toast
						p = int.from_bytes(file.read(4), byteorder='little') #tamanho do campo
						a = GetToastControllerFrame(p, pageName)
						v = a[0:attrLen[i]]
					for j in range(0, len(values)):
						if(meta[i][2] == values[j][0]):
							if(v == values[j][1]):
								now = file.tell()
								file.seek(itemP+2, 0)
								file.write(bytes(1))
								file.seek(now)
								encontrou = True
								break
					if(encontrou):
						break
			# salvando e fechando
			file.close()
			return True
		except IOError:
			print('Error opening '+pageName+str(offset)+self._Extension)
			return False

	def _GetFrames(self, pageName,offset):
		try:
			file = open(self._Directory+pageName+str(offset)+self._Extension, 'rb')
			data = []
			meta = self._GetMeta(pageName)
			metaLen = int(meta[0])
			meta = meta[1:]
			itemLen = 3 + 3*metaLen
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
				attrType = []
				# pegando os tamanhos dos campos
				for i in range(0, metaLen):
					attrType.append(int.from_bytes(file.read(1), byteorder='little'))
					attrLen.append(int.from_bytes(file.read(2), byteorder='little'))
				# pegando a tupla
				file.seek(pointer, 0)
				for i in range(0, metaLen):
					if(attrType[i] == self._Integer): #lendo int
						aux.append(int.from_bytes(file.read(attrLen[i]), byteorder='little')) #tamanho do campo
					elif(attrType[i] == self._Char): # char
						aux.append(file.read(attrLen[i]).decode())
						file.seek(file.tell()+meta[i][1]-attrLen[i], 0)
					elif(attrType[i] == self._Varchar): #varchar
						aux.append(file.read(attrLen[i]).decode())
					elif(attrType[i] == self._Toast):
						p = int.from_bytes(file.read(4), byteorder='little') #tamanho do campo
						a = GetToastControllerFrame(p, pageName)
						aux.append(a[0:attrLen[i]])
				data.append(aux)
			data = list(data)

			return data
		except IOError:
			print('Error opening '+pageName+str(offset)+self._Extension) #página não existe
			return False

	def _CreateMetaPage(self, pageName,attr): # [[type,typeLen,nameLen,name],...] | cria a página com os campos da tupla
		try:
			file = open(self._Directory+pageName+self._MetaData+self._Extension, 'wb')
			# pega os atributos já verificados e insere um por vez
			metaLen = len(attr)
			file.write(metaLen.to_bytes(1,'little')) # quantidade de atributos do meta
			attrLen = 0
			for a in attr:
				file.write(a[0].to_bytes(1,'little')) #tipo do campo
				file.write(a[1].to_bytes(4,'little')) #tamanho do campo
				file.write(a[2].to_bytes(1,'little')) #tamanho do nome
				file.write(a[3].encode()) #pra string
				attrLen += 6 + len(a[3])
			file.write(bytes(self._Length - metaLen - attrLen))
			# salvando e fechando
			file.close()
			return True
		except IOError:
			print('Error creating '+pageName+self._MetaData+self._Extension) #não deu pra criar a página
			return False

	def _GetMeta(self, pageName): #pegar os atributos da tabela
		try:
			file = open(self._Directory+pageName+self._MetaData+self._Extension, 'rb')
			attr = []
			metaLen = int.from_bytes(file.read(1), byteorder='little') # tamanho do meta
			attr.append(metaLen)
			for i in range(0, metaLen):
				v = []
				a = int.from_bytes(file.read(1), byteorder='little') #tipo do primeiro campo, se não existir retorna um vetor vazio
				v.append(a)
				a = int.from_bytes(file.read(4), byteorder='little') #tamanho do campo
				v.append(a)
				a = int.from_bytes(file.read(1), byteorder='little')#tamanho do nome do campo
				a = file.read(a).decode()
				v.append(a)
				attr.append(v)
			file.close()
			return attr
		except IOError:
			print('Error opening '+pageName+self._MetaData+self._Extension) #página não existe
			return False

	# TOAST SECTION #

	def _CreateToastControllerPage(self, pageName, offset,LastUsedPage = 0):
		try:
			file = open(self._Directory+pageName+str(offset)+self._ToastController+self._Extension, 'w+b')
			headerBytes = 10
			# criando o header
			pd_lower = headerBytes # Offset para começar o espaço livre
			ListLength = 0
			LastID = 0
			file.write(pd_lower.to_bytes(2,'little'))
			file.write(ListLength.to_bytes(2,'little'))
			file.write(LastUsedPage.to_bytes(2,'little'))
			file.write(LastID.to_bytes(4,'little'))
			# inicializando espaços vazios
			free = self._Length - headerBytes # bytes livres
			file.write(bytes(free))
			# salvando e fechando
			file.close()
			return True
		except IOError:
			print('Error creating '+pageName+str(offset)+self._ToastController+self._Extension)
			return False

	def _CreateToastPage(self, pageName, offset):
		try:
			file = open(self._Directory+pageName+str(offset)+self._ToastContent+self._Extension, 'w+b')
			headerBytes = 2
			# criando o header
			pd_lower = headerBytes # Offset para começar o espaço livre
			file.write(pd_lower.to_bytes(2,'little'))
			# inicializando espaços vazios
			free = self._Length - headerBytes # bytes livres
			file.write(bytes(free))
			# salvando e fechando
			file.close()
			return True
		except IOError:
			print('Error creating '+pageName+str(offset)+self._ToastContent+self._Extension)
			return False

	def _CreateToastControllerFrame(self, pageName, offset, text):
		try:
			file = open(self._Directory+pageName+str(offset)+self._ToastController+self._Extension, 'r+b')
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

			if((self._Length - pd_lower) < (tupleLen)): # se não há espaço
				file.close()
				CreateToastControllerPage(pageName, offset+1, lastUsedPage) # cria uma nova página
				return CreateToastControllerFrame(pageName, offset+1, text) # insere a tupla na nova página

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
			file.write(LastUsedself._to_bytes(2, 'little'))

			# criando o item
			file.seek(pd_lower, 0)
			file.write(tupleId.to_bytes(4, 'little'))
			file.write(tupleself._to_bytes(2, 'little'))
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
			print('Error opening '+pageName+str(offset)+self._ToastController+self._Extension)
			return False

	def _CreateToastFrame(self, pageName,offset,text):
		try:
			file = open(self._Directory+pageName+str(offset)+self._ToastContent+self._Extension, 'r+b')
			# verificando se há espaço na página
			pd_lower = int.from_bytes(file.read(2), 'little') # lendo o ponteiro que indica onde colocar o próximo item
			tupleLen = len(text)
			if(tupleLen <= (self._Length - pd_lower)):
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

			remaining = self._Length - pd_lower
			if(remaining == 0):
				file.close() #salvando e fechando
				return CreateToastFrame(pageName, offset+1, text)
			insert = text[0:remaining]
			file.seek(pd_lower, 0) # posição de início do pd_lower
			file.write(insert.encode()) #inserindo o que dá
			file.seek(0,0) #atualizando pd_lower pro máximo
			file.write((self._Length).to_bytes(2, 'little'))

			CreateToastPage(pageName, offset+1) # cria uma nova página
			file.close() #salvando e fechando

			aux = []
			aux.append(pd_lower)
			aux.append(offset)
			aux.append(CreateToastFrame(pageName, offset+1, text[remaining:])[2])
			return aux
		except IOError:
			print('Error opening '+pageName+str(offset)+self._ToastContent+self._Extension)
			return False

	def _GetToastControllerFrame(self, id, pageName, offset = 0):
		file = open(self._Directory+pageName+str(offset)+self._ToastController+self._Extension, 'r+b')

		file.seek(2,0)
		ListLength = int.from_bytes(file.read(2), byteorder='little')
		file.seek(10,0)
		for a in range(0,ListLength):
			aux = 10 + 12*a
			file.seek(aux,0)
			idAtual = int.from_bytes(file.read(4), byteorder='little')
			if(id == idAtual):
				page = int.from_bytes(file.read(2), byteorder='little')
				pointer = int.from_bytes(file.read(2), byteorder='little')
				size = 1+int.from_bytes(file.read(4), byteorder='little')
				file.close()
				return GetToastFrame(pageName,page,pointer,size)

		file.close()
		return GetToastControllerFrame(id, pageName, offset+1)


	def _GetToastFrame(self, pageName,offset,pointer,size,text = ''): #envie text como ''
		try:
			file = open(self._Directory+pageName+str(offset)+self._ToastContent+self._Extension, 'r+b')

			file.seek(pointer, 0)

			if(size <= (self._Length - pointer)):
				a = file.read(size).decode()
				file.close()
				return a

			remaining = size - (self._Length - pointer)
			text = text + file.read(remaining).decode()
			size = size - remaining
			file.close() #salando e fechando
			return GetToastFrame(pageName,offset+1,2,size,text)
		except IOError:
			print('Error opening '+pageName+str(offset)+self._ToastContent+self._Extension)
			return False
