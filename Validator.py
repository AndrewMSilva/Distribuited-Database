
def Read(cmd=False):
    # acionando valiadores
    if(cmd != ''):
        if(cmd[0:12] == 'create table'):
            cmd = CreateTable(cmd[12:])
        elif(cmd[0:11] == 'insert into'):
            cmd = InsertInto(cmd[11:])
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
    if(cmd[0] != ' '):
        return False
    i = 1
    status = -1
    attr = [1,False]
    values = []
    for j in range(i,len(cmd)):
        if(status == -1 and cmd[j] != ' '): # procurando onde começa o nome da tabela
            status = 0
            i = j
        elif(status == 0 and (cmd[j] == ' ' or cmd[j+1] == '(')): # procurando onde termina o nome da tabela
            attr[1] = cmd[i:j+1]
            attr[1] = attr[1].split(' ')[0]
            status = 1
        elif(status == 1 and (cmd[j] == '(' or cmd[j-1] == '(')): # procurando onde começa os argumentos
            i = j+1
            status = 2
        elif(status == 2):
            cmd = cmd[j:len(cmd)-1].split(',') # separando os argumentos pela vírgula
            for i in range(0,len(cmd)):
                a = cmd[i].split("'") # separando pelas aspas pra conferir o tipo
                if(len(a) == 1):
                    values.append(int(cmd[i]))
                else:
                    values.append(a[1])

            break
    if(not values[0]):
        return False
    attr.append(values)
    return attr

def DeleteFrom(cmd):
    if(cmd[0] != ' '):
        return False
    i = 1
    status = -1
    attr = [2,False]
    for j in range(i,len(cmd)):
        if(status == -1 and cmd[j] != ' '): # procurando onde começa o nome da tabela
            status = 0
            i = j
        elif(status == 0 and (cmd[j] == ' ' or cmd[j+1] == '(')): # procurando onde termina o nome da tabela
            attr[1] = cmd[i:j]
            attr[1] = attr[1].split(' ')[0]
            status = 1
        elif(status == 1 and (cmd[j] == '(' or cmd[j-1] == '(')): # procurando onde começa os argumentos
            i = j+1
            status = 2
        elif(status == 2):
            attr.append(int(cmd[j:len(cmd)-1]))
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
            print(cmd[j])
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
