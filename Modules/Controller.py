import Settings.Function as Function
import Settings.Page as Page
import Modules.Validator as Validator
import Modules.Communicator as Communicator
import Modules.PageManager as PageManager

Communicator.Start()

def Execute(cmd):
	cmd = Validator.Read(cmd)

	if(isinstance(cmd,list)):
		if cmd[0] == Function.Include:
			Function.Include(cmd[1])
		elif cmd[0] == Function.CreateTable:
			CreateTable(cmd[1:])
		elif cmd[0] == Function.InsertInto:
			InsertInto(cmd[1:])
		elif cmd[0] == Function.DeleteFrom:
			DeleteFrom(cmd[1:])
		elif cmd[0] == Function.Select:
			Select(cmd[1:])
		elif cmd[0] == Function.ShowTable:
			ShowTable(cmd[1:])

def CreateTable(cmd):
	if(PageManager.PageExist(cmd[0]+'meta')): #se já existe n cria denovo e retorna nada
		print("Table already exists: "+cmd[0])
		return
	values = []
	for a in cmd[1:]: #pega os atributos do comando
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
		else: #caso seja varchar
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
	PageManager.CreateMetaPage(cmd[0],values)
	PageManager.CreatePage(cmd[0],0)
	PageManager.CreateToastPage(cmd[0],0)
	PageManager.CreateToastControllerPage(cmd[0],0)

def InsertInto(cmd):
	if(not PageManager.PageExist(cmd[0], 0)): #se já existe n cria denovo e retorna nada
		print("Table not found: "+cmd[0])
		return

	for values in cmd[1:]:
		PageManager.CreateFrame(cmd[0], 0, values)

def DeleteFrom(cmd): # recebe [2, tableName, [[attr, value],[attr, value]]]
	offset = 0
	while(PageManager.PageExist(cmd[0],offset)):
		PageManager.DeleteFrame(cmd[0], offset, cmd[1])
		offset += 1

def Select(cmd):
	offset = 0
	values = []
	while(PageManager.PageExist(cmd[0],offset)):
		values = values + PageManager.GetFrames(cmd[0],offset)
		offset += 1
	meta = PageManager.GetMeta(cmd[0])
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

def ShowTable(cmd):
	meta = PageManager.GetMeta(cmd[0])
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
