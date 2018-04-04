#   Autor: Andrew Malta
#   Obs: usar Python 3.x
#   Comandos:
#       COMANDO TABELA (ARGUMENTO1, ARGUMENTO2)
#       create table cliente (id int PK, nome varchar(30))
#       insert into cliente ("João", 44768356423)
#       remove from cliente (4) -> 4 é a PK
#		select * from cliente -> lista todos os registros
#		show table cliente -> mostra os campos da tabela
#       exit

import Validator
import PageManager

print('\nWelcome to best SGBD on universe! Enjoy it xD')
print('Based on Postgres 8.0')
while(True):
	cmd = "select        *  from cliente  "
	cmd = "create table cliente (nome char(30), id int PK, sobrenome varchar(12))"
	cmd = "insert into cliente('Antônio NDJSADJS', 8, 'que')"
	cmd = "show table   cliente    "
	cmd = "delete from   cliente   where id  =  2 "
	cmd = "insert into cliente('Antônio hgghfdg', 5, 'que')"
	cmd = "select        *  from cliente  "
	cmd = input('>>> ')
	cmd = Validator.Read(cmd) # valida o comando
	if(isinstance(cmd,list)): # verifica se retornou uma lista
		PageManager.Read(cmd) # executa o comando
		#break # usar apenas para testar um comando específico como parâmetro
