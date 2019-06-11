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

import Modules.Controller as Controller

while(True):
	try:
		cmd = input('')
	except EOFError:
		break
	
	Controller.Execute(cmd) # executa o comando
