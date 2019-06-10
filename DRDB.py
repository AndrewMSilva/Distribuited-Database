#   Database based on Postgres 8.0
# 	Commands:
#       COMMAND      TABLE  (ARGUMENT1, ARGUMENT2)
#       create table cliente (id int, nome varchar(30))
#       insert into cliente (4898, "Joao")
#       delete from cliente where id = 4898
#		select * from cliente -> lista todos os registros
#		show table cliente -> mostra os campos da tabela
#       exit

print('\nWelcome to Distribuited Relational Database!')
import Modules.Communicator as Communicator
import Modules.Validator as Validator
import Modules.Executer as Executer
while(True):
	try:
		cmd = input('>>> ')
	except EOFError:
		break
	# Acionando validadores
	if(cmd != ''):
		splited = (cmd+' ').split()
		if splited[0] == 'include':
			if len(splited) != 2:
				cmd = False
			else:
				Communicator.Include(splited[1])
		elif(splited[0] == 'create' and splited[1] == 'table'):
			cmd = Validator.CreateTable(cmd[12:])
		elif(splited[0] == 'insert' and splited[1] == 'into'):
			cmd = Validator.InsertInto(cmd)
		elif(splited[0] == 'delete' and splited[1] == 'from'):
			cmd = Validator.DeleteFrom(cmd[11:])
		elif(splited[0] == 'select'):
			cmd = Validator.Select(cmd[6:])
		elif(splited[0] == 'show' and splited[1] == 'table'):
			cmd = Validator.ShowTable(cmd[10:])
		elif(splited[0] == 'exit'):
			exit()
		else:
			print('Command not found:', cmd)
			cmd = True

		if not cmd:
			print('Sintax error')

	if(isinstance(cmd,list)): # verifica se retornou uma lista
		Executer.Read(cmd) # executa o comando
