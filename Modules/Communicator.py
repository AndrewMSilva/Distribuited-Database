import Settings.Function as Function
from socket import socket, gethostbyname, gethostname, AF_INET, SOCK_STREAM
from threading import Thread
import hashlib
import random
import time

# Main settings
LocalIP      = gethostbyname(gethostname())
StandardPort = 5918
BufferLength = 1024
LocalID      = 0
Running      = True

# Group settings
Token = hashlib.sha1('Aa@215?'.encode('latin1')).hexdigest()
Group = {}

''' Message methods '''

def EncodeMessage(type, content):
    ts = time.time()
    message = Token + str(type) + str(len(str(ts))) + str(ts) + content
    return message.encode('latin1')

def DecodeMessage(enconded_message):
    token_len = len(Token)
    enconded_message = enconded_message.decode('latin1')
    try:
        token = str(enconded_message[:token_len])
        type = int(enconded_message[token_len:token_len+1])
    except:
        return False
    time_len = int(enconded_message[token_len+2:token_len+4])
    time = float(enconded_message[token_len+4:token_len+4+time_len])
    content = enconded_message[token_len+4+time_len:]
    return {'Token': token, 'Type': type, 'Time': time, 'Content': content}

def SendMessage(ip, content, type):
    enconded_message = EncodeMessage(type, content)
    # Finding the destination
    found = False
    for i in Group:
        if ip == Group[i]:
            found = True
            enconded_message = EncodeMessage(type, content)
            try:
                tcp = socket(AF_INET, SOCK_STREAM)
                tcp.connect((ip, StandardPort))
                tcp.send(enconded_message)
                tcp.close()
            except Exception as e:
                print('Error:', e)
            break
    if not found:
        print('The destination is not a group member')

def ReceiveMessage(conn):
    enconded_message = conn.recv(BufferLength)
    message = DecodeMessage(enconded_message)
    # Verifying the message format
    if not message:
        conn.close()
        return False
    # Authenticating message
    elif message['Token'] != Token:
        print('Access denied: authentication falied')
        conn.close()
        return False
    # Interpreting message
    else:
        return message

''' Group methods '''

def Agroup(ip, id=None, type=Function.Agroup):
    # Verifying the connection is itself
    if ip == LocalIP:
        return
    # Verifying if the connection already exists
    for i in Group:
        if Group[i] == ip:
            return
    # Creating connection
    SendAgroupMessage(ip, type)

    if not id:
        id = len(Group)+1
    Group[id] = ip

def SendAgroupMessage(ip, type=Function.Agroup):
    content = str(LocalID) + ':' + str(len(Group))
    for i in Group:
        if Group[i] != ip:
            content += ' ' + str(i) + ':' + Group[i]['IP']

    enconded_message = EncodeMessage(type, content)
    print('Sending:', enconded_message)
    try:
        tcp = socket(AF_INET, SOCK_STREAM)
        tcp.connect((ip, StandardPort))
        tcp.send(enconded_message)
        tcp.close()
    except Exception as e:
        print('Error:', e)

def Include(ip):
    Agroup(ip, type=Function.Include)

def ShowGroup():
    if not Group:
        print('There aren\'t connections')
    else:
        for i in Group:
            print('ID:', i, 'IP', Group[i])

def UpdateGroup(id, content):
    content = content.split()[1:]
    for ip in content:
        addr = addr.split(':')
        id = addr[0]
        ip = addr[1]
        for i in range(0, len(Group)):
            if ip == LocalIP:
                return
            elif i == len(Group) - 1:
                Agroup(ip, id)


def Connection(conn, addr):
    message = ReceiveMessage(conn)
    if message: 
        if message['Type'] == Function.Agroup or message['Type'] == Function.Include:
            # Verifying the new connection
            content = message['Content'].split()[0].split(':')
            id = int(content[1])
            ip = addr[0]
            for i in Group:
                if ip == Group[i]:
                    conn.close()
                    continue
            # Creating a new connection
            Group[id] = ip
            UpdateGroup(id, message['Content'])
            if message['Type'] == Function.Include:
                LocalID = int(content[2])
    conn.close()

def Listener():
    TCP = socket(AF_INET, SOCK_STREAM)
    TCP.bind((LocalIP, StandardPort))
    print('Listening in', LocalIP+':'+str(StandardPort))
    # Listening for connections
    TCP.listen(1)
    while Running:
        conn, addr = TCP.accept()
        connection = Thread(target=Connection, args=[conn, addr,])
        connection.start()
    TCP.close()

def Start():
    listener = Thread(target=Listener)
    listener.start()

''' DHT methods '''

StorageSpace = 256
Addresses    = [False]*StorageSpace

# Pearson string hash
T = list(range(0, StorageSpace))
random.seed(StorageSpace)
random.shuffle(T)

def GetPointer(file_name):
    h = [0]*StorageSpace
    n = len(file_name)
    for i in range(0, n):
        h[i+1] = T[h[i] ^ ord(file_name[i])]
    return h[n]

print(int(StorageSpace/len(Group)))
def GetIDByFileName(file_name):
    pointer = GetPointer(file_name)
    local_space = int(StorageSpace/len(Group))
    for id in Group:
        if pointer < local_space:
            break
        else:
            local_space += local_space
    print(id, pointer)
    return id

def FileExists(file_name):
    pointer = GetPointer(file_name)
    return Addresses[pointer]