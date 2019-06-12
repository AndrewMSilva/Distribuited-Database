import Settings.Function as Function
from socket import socket, gethostbyname, gethostname, AF_INET, SOCK_STREAM
from threading import Thread
import hashlib
import time

# Main settings
LOCAL_IP = gethostbyname(gethostname())
PORT     = 5918
Running  = True

# Group controllers
TOKEN = hashlib.sha1('Aa@215?'.encode('latin1')).hexdigest()
Group = {}
ID    = 0

# Events controllers
EVENTS = []

# DHT controllers
DHT   = False
Data  = {}

# Massage configs
BUFFER_LEN = 1024
TIMEOUT    = 0.1

# Message types
EVENT        = 3
SET_Data     = 4
GET_Data     = 5
GIVE_Data    = 6
NOT_FOUND    = 404

def Start():
    listener = Thread(target=Listener)
    listener.start()

''' Message methods '''

def EncodeMessage(type, content):
    message = TOKEN + str(type) + content
    return message.encode('latin1')

def DecodeMessage(enconded_message):
    token_len = len(TOKEN)
    enconded_message = enconded_message.decode('latin1')
    try:
        token = str(enconded_message[:token_len])
        type = int(enconded_message[token_len:token_len+1])
    except:
        return False
    content = enconded_message[token_len+1:]
    return {'TOKEN': token, 'Type': type, 'Content': content}

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
                tcp.connect((ip, PORT))
                tcp.send(enconded_message)
                tcp.close()
            except Exception as e:
                print('Error:', e)
            break
    if not found:
        print('The destination is not a group member')

def ReceiveMessage(conn):
    enconded_message = conn.recv(BUFFER_LEN)
    message = DecodeMessage(enconded_message)
    # Verifying the message format
    if not message:
        conn.close()
        return False
    # Authenticating message
    elif message['TOKEN'] != TOKEN:
        print('Access denied: authentication falied')
        conn.close()
        return False
    # Interpreting message
    else:
        return message

''' Group method '''

def Agroup(ip, id=None, type=Function.Agroup):
    # Verifying the connection is itself
    if ip == LOCAL_IP:
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
    content = str(ID) + ':' + str(len(Group))
    for i in Group:
        if Group[i] != ip:
            content += ' ' + str(i) + ':' + Group[i]['IP']

    enconded_message = EncodeMessage(type, content)
    try:
        tcp = socket(AF_INET, SOCK_STREAM)
        tcp.connect((ip, PORT))
        tcp.send(enconded_message)
        tcp.close()
    except Exception as e:
        print('Error:', e)

def Include(ip):
    Agroup(ip, type=Function.Include)

def Group():
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
            if ip == LOCAL_IP:
                return
            elif i == len(Group) - 1:
                Agroup(ip, id)


def Connection(conn, addr):
    while Running:
        message = ReceiveMessage(conn)
        if message: 
            if message['Type'] == Function.Agroup or message['Type'] == Function.Include:
                # Verifying the new connection
                content = message['Content'].split()[0].split(':')
                id = int(content[1])
                ip = addr[0]
                for i in Group:
                    if ip == Group[i]['IP']:
                        conn.close()
                        continue
                # Creating a new connection
                Group[id] = ip
                UpdateGroup(id, message['Content'])
                if message['Type'] == Function.Include:
                    ID = int(content[2])
        conn.close()

def Listener():
    TCP = socket(AF_INET, SOCK_STREAM)
    TCP.bind((LOCAL_IP, PORT))
    print('Listening in', LOCAL_IP+':'+str(PORT))
    # Listening for connections
    TCP.listen(1)
    while Running:
        conn, addr = TCP.accept()
        connection = Thread(target=Connection, args=[conn, addr,])
        connection.start()
    TCP.close()

''' Synchronized events methods '''

def SendEvent(content):
    time_stamp = time.time()
    EVENTS.append((time_stamp, content))
    message = str(time_stamp) + ':' + content
    Broadcast(message, EVENT)

def EncodeEvents():
    if not EVENTS:
        return ''

    content = ''
    for event in EVENTS:
        content += ' ' + str(event[0]) + ':' + event[1]
    return content

def EventsReceived(content):
    content = content.split()
    # Deconding events from message
    for e in content:
        e = e.split(':')
        event = (float(e[0]), e[1])
        # Verifying and adding the event
        if event in EVENTS:
            continue
        else:
            EVENTS.append(event)
            EVENTS.sort(key=lambda e: e[0])

def Events():
    if not EVENTS:
        print('There aren\'t events')
    else:
        print('Current time_stamp:', EVENTS[len(EVENTS)-1][0])
        for event in EVENTS:
            print(event)

''' DHT methods '''

def IdByKey(key):
    total = len(Group)+1
    return key % total

def SetData(key, data):
    if not DHT:
        Data[key] = data
    else:
        id = IdByKey(key)
        if ID == id:
            Data[key] = data
        else:
            SendMessage(Group[id]['IP'], str(key)+':'+str(data), SET_Data)

def GetData(key):
    id = IdByKey(key)
    if ID == id or not DHT:
        print('Data:', Data[key])
    else:
        SendMessage(Group[id]['IP'], str(key), GET_Data)

def GiveData(id, key):
    if key in Data:
        SendMessage(Group[id]['IP'], str(Data[key]), GIVE_Data)
    else:
        SendMessage(Group[id]['IP'], str(NOT_FOUND), GIVE_Data)

def ShowData():
    if not Data:
        print('There aren\'t storaged data')
    for key, content in Data.items():
        print(key, content)