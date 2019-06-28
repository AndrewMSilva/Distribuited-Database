from GroupManager import GroupManager
import random

class StorageManager(GroupManager):
	# Files settings
	_Directory = './Pages/'
	_MetaData  = 'Meta'
	_Extension = '.page'
	_Length    = 8*1024
	# Variable types
	_Integer = 0
	_Char 	 = 1
	_Varchar = 2
	# Values settings
	_MaxStringLen = 255
	# Storage settings
	_Addressement = 1024
	_Storage      = [False]*_Addressement
	__T = list(range(0, _Addressement))
	random.seed(_Addressement)
	random.shuffle(__T)
	# Message types for DHT
	_Result			   = 3
	_CreateMetaPageMessage = 4
	_CreatePageMesssage    = 5

	# DHT SECTION #
	def _GetPointer(self, file_name):
		file_name = file_name
		h = [0]*self._Addressement
		n = len(file_name)
		for i in range(0, n):
			h[i+1] = self.__T[h[i] ^ ord(file_name[i])]
		return h[n]

	def _GetData(self, file_name):
		file_name = file_name
		pointer = self._GetPointer(file_name)
		local_space = int(self._Addressement/len(self._Group))
		for id in sorted(self._Group.keys()):
			if pointer < local_space:
				break
			else:
				local_space += local_space
		return self._Group[id], pointer, self._Storage[pointer]

	def _AddFile(self, file_name):
		file_name = file_name
		pointer = self._GetPointer(file_name)
		if not self._Storage[pointer]:
			self._Storage[pointer] = True
			return True
		else:
			return False

	def _Page(self, prefix, sufix='', extension=_Extension):
		return prefix+str(sufix)+extension
	
	def HandleMessage(self, conn, message):
		print(message)
		if message.type == self._CreateMetaPageMessage:
			result = self._CreateMetaPage(message.data.table_name, message.data.fields)
			enconded_message = self._EncodeMessage(result, self._Result, True)
			conn.send(enconded_message)

	# META PAGE SECTION #

	def _CreateMetaPage(self, table_name, fields):
		file_name = self._Page(table_name, self._MetaData)
		ip, address, used = self._GetData(file_name)
		# Checking if the address is already used
		if used:
			return False
		# Checking if the file need to be created locally
		if ip == self._IP:
			try:
				# Creating file
				file = open(self._Directory+file_name, 'wb')
				# Inserting fields meta data
				metaLen = len(fields)
				file.write(metaLen.to_bytes(1,'little')) # Number of fields
				fieldsLen = 0
				for a in fields:
					file.write(a[0].to_bytes(1,'little')) # Field type
					file.write(a[1].to_bytes(4,'little')) # Field length
					file.write(a[2].to_bytes(1,'little')) # Field name length
					file.write(a[3].encode())			  # Field name
					fieldsLen += 6 + len(a[3])
				file.write(bytes(self._Length - metaLen - fieldsLen))
				# salvando e fechando
				file.close()
				return True
			except IOError:
				return False
		# If the file need to be created in another device:
		else:
			data = {'table_name': table_name, 'fields': fields}
			result = self._SendMessage(ip, data, self._CreateMetaPageMessage, True)
			return result.data

	def _CreatePage(self, file_name):
		try:
			file = open(self._Directory+file_name, 'w+b')
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
			print('Error creating '+file_name+str(offset)+self._Extension)
			return False

	def _CreateFrame(self, file_name, offset, values): # n = o somatório dos bytes da tupla
		try:
			file = open(self._Directory+file_name+str(offset)+self._Extension, 'r+b')
			# calculando somatório de bytes da tupla e verificando os tipos
			tupleLen = 0
			meta = self._GetMeta(file_name)
			metaLen = meta[0]
			meta = meta[1:]
			if(metaLen != len(values)):
				print('Table '+file_name+' have '+str(metaLen)+' attributes')
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
				if(PageExist(file_name, offset+1)): # se existe uma página seguinte
					CreateFrame(file_name, offset+1, values) # tenta inserir na próxima página
				else: # se não existe uma págica seguinte
					CreatePage(file_name, offset+1) # cria uma nova página
					CreateFrame(file_name, offset+1, values) # insere a tupla na nova página
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
				if meta[i][0] == self._Integer: # se for int
					file.write(meta[i][0].to_bytes(1, 'little'))
					file.write(meta[i][1].to_bytes(2, 'little'))
				elif meta[i][0] == self._Char: # se for char
					file.write(meta[i][0].to_bytes(1, 'little'))
					file.write(len(values[i]).to_bytes(2, 'little'))
				elif meta[i][0] == self._Varchar: # se for varchar
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
			# atualizando tamanho da list	print(s)a de itens
			file.seek(10, 0) # posição de início do tlist
			tlist = 1 + int.from_bytes(file.read(2), byteorder='little') # tamanho atual da lista
			file.seek(10, 0) # posição de início do tlist
			file.write(tlist.to_bytes(2, 'little'))

			# salvando e fechando
			file.close()
			return True
		except IOError:
			print('Error opening '+file_name+str(offset)+self._Extension)
			return False

	def _DeleteFrame(self, file_name, offset, values):
		try:
			file = open(self._Directory+file_name+str(offset)+self._Extension, 'r+b')
			meta = self._GetMeta(file_name)
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
			print('Error opening '+file_name+str(offset)+self._Extension)
			return False

	def _GetFrames(self, file_name,offset):
		try:
			file = open(self._Directory+file_name+str(offset)+self._Extension, 'rb')
			data = []
			meta = self._GetMeta(file_name)
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
				data.append(aux)
			data = list(data)

			return data
		except IOError:
			print('Error opening '+file_name+str(offset)+self._Extension) #página não existe
			return False

	def _GetMeta(self, file_name): #pegar os atributos da tabela
		try:
			file = open(self._Directory+file_name+self._MetaData+self._Extension, 'rb')
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
			print('Error opening '+file_name+self._MetaData+self._Extension) #página não existe
			return False