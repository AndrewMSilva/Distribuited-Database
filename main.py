#   Autor: Andrew Malta
#   Obs: usar Python 3.x
#   Comandos:
#       COMANDO TABELA (ARGUMENTO1, ARGUMENTO2)
#       create table cliente (id int PK, nome varchar(30))
#       insert into cliente ("João", 44768356423)
#       remove from cliente (4) -> 4 é a PK
#		select * from cliente -> lista todos os registros
#       exit

import Validator
import PageManager

print('\nWelcome to best SGBD on universe! Enjoy it xD')
print('Based on Postgres 8.0')
while(True):
	cmd = "insert into cliente(1, 'Antônio')"
	cmd = "create table cliente (id int PK, nome varchar(30))"
	cmd = "select    nome ,  id  from cliente"
	#cmd = input('>>> ')
	cmd = Validator.Read(cmd) # valida o comando
	if(isinstance(cmd,list)): # verifica se retornou uma lista
		PageManager.Read(cmd) # executa o comando
		break # usar apenas para testar um comando específico como parâmetro
