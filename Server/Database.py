import PageManager
import Page

def CreateTable(args):
	if(PageManager.PageExist(args[0]+Page.MetaData)): #se já existe n cria denovo e retorna nada
		print("Table already exists: "+args[0])
		return
	values = []
	for a in args[1:]: #pega os atributos do comando
		v = []
		aux = Page.CharMin
		if(a[1] == 'int'): #caso o atributo seja inteiro
			v.append(1)
			v.append(4) #tamanho fixo, mas será desconsiderado
			v.append(len(a[0])) #tamanho do nome do campo
			v.append(a[0]) #nome do campo
		elif(a[1][0:4] == 'char'): #caso seja char
			v.append(2)
			aux = int((a[1].split('(')[1].split(')'))[0])
			v.append(aux) #tamanho do char
			v.append(len(a[0]))#tamanho do nome do campo
			v.append(a[0])#nome do campo
		elif(a[1][0:7] == 'varchar'): #caso seja varchar
			v.append(3)
			aux = int((a[1].split('(')[1].split(')'))[0])
			v.append(aux) #tamanho do varchar
			v.append(len(a[0])) #tamanho do nome do campo
			v.append(a[0]) #nome do campo
		if(aux < Page.CharMin or aux > Page.CharMax):
			print('Varchar size is '+str(Page.CharMin)+' to '+str(Page.CharMax))
			return
		values.append(v)
	if(len(values) > Page.AttrMaxNum):
		print('Maximum of attributes is '+str(Page.AttrMaxNum))
		return
	PageManager.CreateMetaPage(args[0],values)
	PageManager.CreatePage(args[0],0)
	PageManager.CreateToastPage(args[0],0)
	PageManager.CreateToastControllerPage(args[0],0)

def InsertInto(args):
	if(not PageManager.PageExist(args[0], 0)): #se já existe n cria denovo e retorna nada
		print("Table not found: "+args[0])
		return

	for values in args[1:]:
		PageManager.CreateFrame(args[0], 0, values)

def DeleteFrom(args): # recebe [2, tableName, [[attr, value],[attr, value]]]
	offset = 0
	while(PageManager.PageExist(args[0],offset)):
		PageManager.DeleteFrame(args[0], offset, args[1])
		offset += 1

def Select(args):
	offset = 0
	values = []
	while(PageManager.PageExist(args[0],offset)):
		values = values + PageManager.GetFrames(args[0],offset)
		offset += 1
	meta = PageManager.GetMeta(args[0])
	aux = '\n| # | '
	for a in range(1, len(meta)):
		aux = aux + meta[a][2] + ' | '
	print(aux)
	for i in range(0,len(values)):
		aux = '| '+str(i+1)
		for j in range(0,len(values[i])):
			aux = aux +' | '+ str(values[i][j])
		print(aux+' |')
	return

def ShowTable(args):
	meta = PageManager.GetMeta(args[0])
	print(args[0]+' attributes:')
	for a in meta[1:]:
		s = a[2]+' '
		if(a[0] == 1):
			s += 'int'
		elif(a[0] == 2):
			s += 'char('+str(a[1])+')'
		elif(a[0] == 3):
			s += 'varchar('+str(a[1])+')'
		print(s)
