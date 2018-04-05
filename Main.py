#   Autor: Andrew Malta e Gabriel Vassoler
#   Obs: usar Python 3.x
#   Comandos:
#       COMANDO TABELA (ARGUMENTO1, ARGUMENTO2)
#       create table cliente (id int, nome varchar(30))
#       insert into cliente (4898, "João")
#       delete from cliente where id = 4898
#		select * from cliente -> lista todos os registros
#		show table cliente -> mostra os campos da tabela
#       exit

import Validator
import Executer

print('\nWelcome to best SGBD on universe! Enjoy it xD')
print('Based on Postgres 8.0')
while(True):
	cmd = "select        *  from cliente  "
	cmd = "create table cliente (nome char(30), id int PK, sobrenome varchar(12))"
	cmd = "insert into cliente('Antônio NDJSADJS', 8, 'que')"
	cmd = "show table   cliente    "
	cmd = "delete from   cliente   where id  =  2 "
	cmd = "insert into cliente('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam sodales non metus sit amet condimentum. Phasellus sed nisi eu magna blandit feugiat in et nulla. Nunc tempus nunc convallis, ultrices ipsum in, eleifend orci. Phasellus nec leo augue. Etiam amet. ', 8, 'que')"
	cmd = "select        *  from cliente  "
	#cmd = input('>>> ')
	cmd = Validator.Read(cmd) # valida o comando
	if(isinstance(cmd,list)): # verifica se retornou uma lista
		Executer.Read(cmd) # executa o comando
		break # usar apenas para testar um comando específico como parâmetro
