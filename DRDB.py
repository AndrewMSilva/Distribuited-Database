#   Database based on Postgres 8.0
# 	Commands:
#       COMMAND      TABLE  (ARGUMENT1, ARGUMENT2)
#       create table cliente (id int, nome varchar(30))
#       insert into cliente (4898, "Joao")
#       delete from cliente where id = 4898
#		select * from cliente -> lista todos os registros
#		show table cliente -> mostra os campos da tabela
#       exit

print('\nWelcome to Distribuited Relational Database, enjoy it!')
import Modules.Validator as Validator
import Modules.Executer as Executer
import Modules.Communicator as Communicator
while(True):
	try:
		cmd = input('>>> ')
	except EOFError:
		break
	cmd = Validator.Read(cmd) # valida o comando
	if(isinstance(cmd,list)): # verifica se retornou uma lista
		Executer.Read(cmd) # executa o comando
