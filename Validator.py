from pyparsing import *

def Read(cmd=False):
    # acionando valiadores
    if(cmd != ''):
        if(cmd[0:12] == 'create table'):
            cmd = CreateTable(cmd[12:])
        elif(cmd[0:11] == 'insert into'):
            cmd = InsertInto(cmd)
        elif(cmd[0:11] == 'delete from'):
            cmd = DeleteFrom(cmd[11:])
        elif(cmd[0:6] == 'select'):
            cmd = Select(cmd[6:])
        elif(cmd[0:10] == 'show table'):
            cmd = ShowTable(cmd[10:])
        elif(cmd == 'exit'):
            exit()
        else:
            print('Command not found:',cmd)
            return False
        if(not cmd):
            print('Sintax error')

        return cmd

def CreateTable(cmd):
    if(cmd == '' or cmd[0] != ' '):
        return False
    i = 1
    status = -1
    attr = [0,False]
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
        # Object names and numbers match these regular expression
        object_name = Regex('[a-zA-Z_]+')
        number = Regex('-?[0-9]+')
        # A string is just something with quotes around it - PyParsing has a built in
        string = QuotedString("'") | QuotedString('"')

        # A term is a number or a string
        term = number | string

        # The values we want to capture are either delimited lists of expressions we know about...
        term_list = (delimitedList(term)).setResultsName('terms')

        # Or just an expression we know about by itself
        table_name = object_name.setResultsName('table')

        # And an SQL statement is just all of these pieces joined together with some string between them
        sql_stmt = "insert into " + table_name + "(" + term_list + ")"

        res = sql_stmt.parseString(cmd)
        query = [1, res.table, list(res.terms)]

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
    attr = [2,False]
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
    attr = [3,False]
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
    attr = [4,False]
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
