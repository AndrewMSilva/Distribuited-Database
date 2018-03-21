def CreatePage(pageName,offset):
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

def CreateMetaPage(pageName,attr): # [[type,typeLen,nameLen,name],...]
	try:
		file = open('__pages__/'+pageName+'meta.dat', 'wb')
		pageLen = 8*1024 # 8KB
		special = 4 # bytes do frame especial
		headerBytes = 12
		# criando o header
		for a in attr:
			file.write(a[0].to_bytes(1,'little'))
			file.write(a[1].to_bytes(1,'little'))
			file.write(a[2].to_bytes(1,'little'))
			file.write(a[3].encode())
		# salvando e fechando
		file.close()
		return True
	except IOError:
		print('Error creating '+pageName+'.dat')
		return False
