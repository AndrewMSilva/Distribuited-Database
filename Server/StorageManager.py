from GroupManager import GroupManager
from threading import Lock
import random
import pickle
import base64
from os import remove

class StorageManager(GroupManager):
	# Files settings
	_Directory = './Pages/'
	_MetaData  = '_META'
	_Extension = '.page'
	_Length    = 8*1024
	# Variable types
	_Integer = 0
	_Char 	 = 1
	_Varchar = 2
	# Values settings
	_MaxStringLen = 255
	# Storage settings
	_Addressement    = 1024
	_Storage		 = [None]*_Addressement
	__StorageLock	 = Lock()
	__StorageConfigs = 'Storage.config'
	_InsertFileMessage = 'insert_file'
	# DHT settings
	__T = list(range(0, _Addressement))
	random.seed(_Addressement)
	random.shuffle(__T)
	# Message types for DHT
	_ResultMessage		   = 'result'
	_CreateMetaPageMessage = 'create_meta_page'
	_GetMetaMessage 	   = 'get_meta'
	_CreatePageMessage     = 'create_page'
	_CreateFrameMassege	   = 'create_frame'
	_RedistributeMessage   = 'redistribute'

	# DHT SECTION #
	def __PearsonHash(self, file_name):
		file_name = file_name
		h = [0]*self._Addressement
		n = len(file_name)
		for i in range(0, n):
			h[i+1] = self.__T[h[i] ^ ord(file_name[i])]
		return h[n]
	
	def __GetIPByPointer(self, pointer, group=None):
		if group is None:
			group = self._Group
		local_space = int(self._Addressement/len(group))
		for ip in group:
			if pointer < local_space:
				break
			else:
				local_space += local_space
		return ip
	
	def __GetPointer(self, file_name, only_available=False):
		backward = False
		initial_pointer = self.__PearsonHash(file_name)
		pointer = initial_pointer
		while True:
			if pointer >= self._Addressement:
				backward = True
				pointer = initial_pointer - 1
			elif pointer < 0:
				return None
			elif self._Storage[pointer] is None and only_available:
				return pointer
			elif self._Storage[pointer] == file_name and only_available:
				return None
			elif self._Storage[pointer] == file_name and not only_available:
				return pointer
			elif backward:
				pointer -= 1
			else:
				pointer += 1

	def _FileExists(self, file_name):
		pointer = self.__GetPointer(file_name)
		if pointer is None:
			return False
		else:
			return True

	def _InsertFile(self, pointer, file_name, broadcast=True):
		self.__StorageLock.acquire()
		try:
			self._Storage[pointer] = file_name
			self.__SaveStorage()
			if broadcast:
				data = {'pointer': pointer, 'file_name': file_name}
				self._GroupBroadcast(data, self._InsertFileMessage)
		finally:
			self.__StorageLock.release()
	
	def __GetStorage(self):
		try:
			file = open(self._ConfigsDirectory+self.__StorageConfigs, 'rb')
			storage = pickle.load(file)
			file.close()
			self._Storage = storage.copy()
			return True
		except:
			return False

	def __SaveStorage(self):
		try:
			file = open(self._ConfigsDirectory+self.__StorageConfigs, 'wb')
			pickle.dump(self._Storage, file)
			file.close()
			print('Storage updated')
			return True
		except:
			return False
	
	def _InitializeStorage(self):
		if not self.__GetStorage():
			self.__SaveStorage()

	def _Page(self, prefix, sufix='', extension=_Extension):
		return prefix+str(sufix)+extension
	
	def _RedistributeFiles(self, old_group, exiting=False):
		for pointer in range(0, self._Addressement):
			file_name = self._Storage[pointer]
			if isinstance(file_name, str):
				old_ip = self.__GetIPByPointer(pointer, old_group)
				if exiting and self._IP in old_group:
					old_group.remove(self._IP)
					current_ip = self.__GetIPByPointer(pointer, old_group)
				else:
					current_ip = self.__GetIPByPointer(pointer)
				if old_ip == self._IP and old_ip != current_ip:
					try:
						file = open(self._Directory+file_name, 'rb')
						content = base64.b64encode(file.read(self._Length))
						file.close()
						data = {'file_name': file_name, 'content': content}
						if self._SendMessage(current_ip, data, self._RedistributeMessage, True):
							remove(self._Directory+file_name)
					except IOError:
						continue
					except Exception as e:
						print('Error redistributing '+file_name+':', e)
	
	def 
	
	def _SaveFile(self, file_name, content):
		try:
			content = base64.b64decode(content)
			file = open(self._Directory+file_name, 'wb')
			file.write(content)
			file.close()
			return True
		except IOError:
			return False
	
	def _ClearStorage(self):
		self._Storage = [None]*self._Addressement
		self.__SaveStorage()
	
	def _OverrideStorage(self, storage):
		self._Storage = storage.copy()
		self.__SaveStorage()

	# META PAGE SECTION #

	def _CreateMetaPage(self, table_name, fields):
		file_name = self._Page(table_name, self._MetaData)
		# Getting an available pointer or stopping if it does not exists
		pointer = self.__GetPointer(file_name, True)
		if pointer is None:
			return False
		# Checking if the file need to be created locally
		ip = self.__GetIPByPointer(pointer)
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
				self._InsertFile(pointer, file_name)
				return True
			except IOError:
				return False
		# If the file need to be created in another device:
		else:
			data = {'table_name': table_name, 'fields': fields}
			result = self._SendMessage(ip, data, self._CreateMetaPageMessage, True)
			if isinstance(result, dict):
				return result['data']
			else:
				result
	
	def _GetMeta(self, table_name):
		file_name = self._Page(table_name, self._MetaData)
		# Getting an available pointer or stopping if it does not exists
		pointer = self.__GetPointer(file_name)
		if pointer is None:
			return False
		# Checking if the file need to be created locally
		ip = self.__GetIPByPointer(pointer)
		if ip == self._IP:
			try:
				file = open(self._Directory+file_name, 'rb')
				fields = []
				metaLen = int.from_bytes(file.read(1), byteorder='little')
				fields.append(metaLen)
				for i in range(0, metaLen):
					v = []
					# Getting field type
					a = int.from_bytes(file.read(1), byteorder='little')
					v.append(a)
					# Getting field length
					a = int.from_bytes(file.read(4), byteorder='little')
					v.append(a)
					# Getting field name
					a = int.from_bytes(file.read(1), byteorder='little')
					a = file.read(a).decode()
					v.append(a)
					fields.append(v)
				file.close()
				return fields
			except IOError:
				return False
		else:
			data = {'table_name': table_name}
			result = self._SendMessage(ip, data, self._GetMetaMessage, True)
			if isinstance(result, dict):
				return result['data']
			else:
				result

	# PAGE SECTION #

	def _CreatePage(self, table_name, offset):
		file_name = self._Page(table_name, offset)
		# Getting an available pointer or stopping if it does not exists
		pointer = self.__GetPointer(file_name, True)
		if pointer is None:
			return False
		# Checking if the file need to be created locally
		ip = self.__GetIPByPointer(pointer)
		if ip == self._IP:
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
				self._InsertFile(pointer, file_name)
				return True
			except IOError:
				return False
		else:
			data = {'table_name': table_name, 'offset': offset}
			result = self._SendMessage(ip, data, self._CreatePageMessage, True)
			if isinstance(result, dict):
				return result['data']
			else:
				result


	def _CreateFrame(self, table_name, offset, values):
		file_name = self._Page(table_name, offset)
		# Getting an available pointer or stopping if it does not exists
		pointer = self.__GetPointer(file_name)
		if pointer is None:
			return False
		# Checking if the file need to be created locally
		ip = self.__GetIPByPointer(pointer)
		if ip == self._IP:
			try:
				file = open(self._Directory+file_name, 'r+b')
				# Checking the types of the received values
				tupleLen = 0
				meta = self._GetMeta(table_name)
				if not meta:
					return False
				metaLen = meta[0]
				meta = meta[1:]
				if(metaLen != len(values)):
					file.close()
					return table_name+' has '+str(metaLen)+' attributes, but received '+str(len(values))
				for i in range(0,metaLen):
					if(meta[i][0] == self._Integer and isinstance(values[i], int)): # se ambos int
						tupleLen += meta[i][1]
					elif(meta[i][0] == self._Char and isinstance(values[i], str)): # se char e str
						if(meta[i][1] > self._MaxStringLen):
							tupleLen += 4
						elif(len(values[i]) <= meta[i][1]):
							tupleLen += meta[i][1]
						else:
							file.close()
							return 'Expected a char('+str(meta[i][1])+'), but received '+str(len(values[i]))+' characteres'
					elif(meta[i][0] == self._Varchar and isinstance(values[i], str)): # se varchar e str
						if(len(values[i]) > self._MaxStringLen):
							tupleLen += 4
						elif(len(values[i]) <= meta[i][1]):
							tupleLen += len(values[i])
						else:
							file.close()
							return 'Expected a varchar('+str(meta[i][1])+'), but has received '+str(len(values[i]))+' characteres'
					else:
						file.close()
						return 'Entry and type are not matching'
				# Getting page available space
				# pd_lower: where insert a new item
				file.seek(4, 0)
				pd_lower = int.from_bytes(file.read(2), 'little')
				file.seek(6, 0) # pd_upper: where insert a new tuple
				pd_upper = int.from_bytes(file.read(2), 'little')
				itemLen = 3 + 3*len(values)
				# If the available space is not enough
				if((pd_upper - pd_lower) < (tupleLen + itemLen)):
					file.close()
					# Try to insert into the next page (if it exists)
					if self.__GetPointer(self._Page(table_name, offset+1)):
						self._CreateFrame(table_name, offset+1, values)
					# If this is the last page, create a new page and insert there the new tuple
					elif self._CreatePage(table_name, offset+1):
						return self._CreateFrame(table_name, offset+1, values)
					else:
						return False
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
				return False
		else:
			data = {'table_name': table_name, 'offset': offset, 'values': values}
			result = self._SendMessage(ip, data, self._CreateFrameMassege, True)
			if isinstance(result, dict):
				return result['data']
			else:
				result