#   Autor: Andrew Malta
#   Obs: usar Python 3.x
#   Comandos:
#       COMANDO TABELA (ARGUMENTO1, ARGUMENTO2)
#       create table cliente (int id PK, varchar[30] nome)
#       insert into cliente ("João", 44768356423)
#       remove from cliente (4) -> 4 é a PK
#		list cliente -> lista todos os registros
#       exit

import Validator
import PageManager

print('\nWelcome to best db on universe! Enjoy it xD')
print('Based on Postgres 8.0')
while(True):
	PageManager.getMeta('clinte')
	cm1 = "insert into clinte('batata','banana')"
	cm1 = "create table clinte (int id PK, varchar[30] nome)"
	cm1 = "create table clinte (int id PK, varchar[30] nome)"
	# cmd = input('>>> ')
	cm1 = Validator.Read(cm1) # valida o comando
	if(isinstance(cm1,list)): # verifica se retornou uma lista
		PageManager.Read(cm1) # executa o comando
		break # usar apenas para testar um comando específico como parâmetro
	elif(cmd): # se não for uma lista mas o resultado for True, o programa vai fechar (usado para o comando exit)
		break
