import Settings.Function as Function
from pyparsing import *

def Read(cmd):
    # Acionando validadores
    if(cmd):
        splited = (cmd+' ').split()
        if splited[0] == 'include':
            if len(splited) != 2:
                cmd = False
            else:
                cmd = [Function.Include, splited[1]]
        elif splited[0] == 'show' and splited[1] == 'group':
            if len(splited) != 2:
                cmd = False
            else:
                cmd = [Function.ShowGroup]
        elif splited[0] == 'quit' and splited[1] == 'group':
            if len(splited) != 2:
                cmd = False
            else:
                cmd = [Function.QuitGroup]
        elif(splited[0] == 'create' and splited[1] == 'table'):
            cmd = CreateTable(cmd[12:])
        elif(splited[0] == 'insert' and splited[1] == 'into'):
            cmd = InsertInto(cmd)
        elif(splited[0] == 'delete' and splited[1] == 'from'):
            cmd = DeleteFrom(cmd[11:])
        elif(splited[0] == 'select'):
            cmd = Select(cmd[6:])
        elif(splited[0] == 'show' and splited[1] == 'table'):
            cmd = ShowTable(cmd[10:])
        elif(splited[0] == 'exit'):
            exit()
        else:
            print('Command not found:', cmd)
            return False

        if not cmd:
            print('Sintax error')
            return False
    
    return cmd

def CreateTable(cmd):
    if(cmd == '' or cmd[0] != ' '):
        return False
    i = 1
    status = -1
    attr = [Function.CreateTable, False]
    for j in range(i,len(cmd)):
        if(status == -1 and cmd[j] != ' '): # procurando onde começa o nome da tabela
            status = 0
            i = j
        elif(status == 0 and (cmd[j] == ' ' or cmd[j] == '(')): # procurando onde termina o nome da tabela
            attr[1] = cmd[i:j]
            attr[1] = attr[1].split(' ')[0]
            status = 1
        elif(status == 1 and cmd[j-1] == '('): # procurando onde começa os argumentos
            i = j+1
            status = 2
        elif(status == 2):
            cmd = cmd[j-1:len(cmd)-1].split(',') # separando os argumentos pela vírgula
            e = False
            for i in range(0,len(cmd)):
                a = cmd[i].split(' ') # separando tags por espaço
                a = list(filter(('').__ne__, a)) # eliminando espaços sobrando
                if(len(a) < 2 or (a[1] != 'int' and a[1][0:4] != 'char' and a[1][0:7] != 'varchar')): # validando os tipos
                    e = True
                    break
                attr.append(a)

            if(e):
                return False
            break
    if(not attr[1]):
        return False
    return attr

def InsertInto(cmd):
    try:
        # Definindo tipos aceitos
        object_name = Regex('[a-zA-Z_]+')
        number = Regex('-?[0-9]+')
        string = QuotedString("'") | QuotedString('"')
        term = number | string # número ou string
        # Definindo expressões regulares
        term_list = (delimitedList(term)).setResultsName('terms')
        table_name = object_name.setResultsName('table')
        # Validando SQL
        sql_stmt = "insert into " + table_name + "(" + term_list + ")"
        res = sql_stmt.parseString(cmd)
        query = [Function.InsertInto, res.table, list(res.terms)]
        for i in range(0, len(query[2])):
            try:
                query[2][i] = int(query[2][i])
            except ValueError:
                continue
        return query
    except ParseException as pe:
        return False

def DeleteFrom(cmd):
    if(cmd[0] != ' '):
        return False
    i = 1
    status = -1
    attr = [Function.DeleteFrom, False]
    values = []
    for j in range(i,len(cmd)):
        if(status == -1 and cmd[j] != ' '): # procurando onde começa o nome da tabela
            status = 0
            i = j
        elif(status == 0 and cmd[j-5:j] == 'where'): # procurando o 'where'
            attr[1] = cmd[i:j-6]
            attr[1] = attr[1].split(' ')[0]
            status = 1
        elif(status == 1 and (cmd[j] != ' ')): # procurando onde começa os argumentos
            s = cmd[j:].split(',');
            for a in s:
                v = a.split('=')
                v[0] = v[0].split(' ')[0]
                if(v[1].find("'") == -1):
                    v[1] = int(v[1])
                else:
                    v[1] = v[1].cmd[i].split("'")[0]
                values.append(v)
            attr.append(values)
            break
    if(not attr[0]):
        return False
    return attr

def Select(cmd):
    if(cmd[0] != ' '):
        return False
    i = 1
    attr = [Function.Select, False]
    status = 0
    for j in range(i,len(cmd)):
        if(status == 0 and cmd[j] != ' '): # procurando onde começam os campos
            i = j
            status = 1
        elif(status == 1 and cmd[j-4:j] == 'from'): #procurando o 'from'
            c = cmd[i:j-5]
            c = c.split(',')
            for i in range(0,len(c)):
                c[i] = c[i].replace(" ", "") # removendo espaços
            attr.append(c)
            status = 2
        elif(status == 2 and cmd[j] != ' '): # procurando onde começa o nome da tabela
            status = 3
            i = j
        elif(status == 3 and (cmd[j] == ' ' or (j+1) == len(cmd))): # procurando onde termina o nome da tabela
            attr[1] = cmd[i:j+1]
            attr[1] = attr[1].split(' ')[0]
            status = 4
    if(not attr[0]):
        return False
    return attr # [3, tableName, [campos...]]

def ShowTable(cmd):
    if(cmd[0] != ' '):
        return False
    i = 1
    status = 0
    attr = [Function.ShowTable, False]
    for j in range(i,len(cmd)):
        if(status == 0 and cmd[j] != ' '): # procurando onde começa o nome da tabela
            status = 1
            i = j
        elif(status == 1 and (cmd[j] == ' ' or (j+1) == len(cmd))): # procurando onde termina o nome da tabela
            attr[1] = cmd[i:j+1]
            attr[1] = attr[1].split(' ')[0]
    if(not attr[0]):
        return False
    return attr
