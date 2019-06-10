from socket import socket, gethostbyname, gethostname, AF_INET, SOCK_STREAM
from threading import Thread
import hashlib
import time

# Main settings
LOCAL_IP = gethostbyname(gethostname())
PORT     = 5050
RUNNING  = True

# Group controllers
PASSWORD = hashlib.sha1('Aa@215?'.encode('latin1')).hexdigest()
ID       = 0
GROUP    = {}

# Events controllers
EVENTS = []

# DHT controllers
DHT   = False
DATA  = {}

# Massage configs
BUFFER_LEN = 1024
TIMEOUT    = 0.1

# Message types
INCLUDE   = 1
AGROUP    = 2
EVENT     = 3
SET_DATA  = 4
GET_DATA  = 5
GIVE_DATA = 6
NOT_FOUND = 404

''' Message methods '''

def EncodeMessage(type, content):
    message = PASSWORD + str(type) + content
    return message.encode('latin1')

def DecodeMessage(enconded_message):
    token_len = len(PASSWORD)
    enconded_message = enconded_message.decode('latin1')
    try:
        token = str(enconded_message[:token_len])
        type = int(enconded_message[token_len:token_len+1])
    except:
        return False
    content = enconded_message[token_len+1:]
    return {'Password': token, 'Type': type, 'Content': content}

def SendMessage(ip, content, type):
    enconded_message = EncodeMessage(type, content)
    # Finding the destination
    found = False
    for i in GROUP:
        if ip == GROUP[i]:
            found = True
            enconded_message = EncodeMessage(type, content)
            tcp = socket(AF_INET, SOCK_STREAM)
            tcp.connect((ip, PORT))
            tcp.send(enconded_message)
            tcp.close()
            break
    if not found:
        print('The destination is not a group member')

def Broadcast(content, type):
    enconded_message = EncodeMessage(type, content)
    for i in GROUP:
        GROUP[i]['OutputQueue'].append(enconded_message)

def ReceiveMessage(conn):
    enconded_message = conn.recv(BUFFER_LEN)
    message = DecodeMessage(enconded_message)
    # Verifying the message format
    if not message:
        conn.close()
        return False
    # Authenticating message
    elif message['Password'] != PASSWORD:
        print('Access denied: authentication falied')
        conn.close()
        return False
    # Interpreting message
    else:
        return message

''' Group method '''

def Agroup(ip, id=None, type=AGROUP):
    # Verifying the connection is itself
    if ip == LOCAL_IP:
        return
    # Verifying if the connection already exists
    for i in GROUP:
        if GROUP[i] == ip:
            return
    # Creating connection
    SendAgroupMessage(ip, type)

    if not id:
        id = len(GROUP)+1
    GROUP[id] = ip

def SendAgroupMessage(ip, type=AGROUP):
    content = str(ID) + ':' + str(len(GROUP))
    for i in GROUP:
        if GROUP[i] != ip:
            content += ' ' + str(i) + ':' + GROUP[i]['IP']

    enconded_message = EncodeMessage(type, content)
    try
    tcp = socket(AF_INET, SOCK_STREAM)
    tcp.connect((ip, PORT))
    tcp.send(enconded_message)
    tcp.close()

def Include(ip):
    Agroup(ip, type=INCLUDE)

def Group():
    if not GROUP:
        print('There aren\'t connections')
    else:
        for i in GROUP:
            print('ID:', i, 'IP', GROUP[i])

def UpdateGroup(id, content):
    content = content.split()[1:]
    for ip in content:
        addr = addr.split(':')
        id = addr[0]
        ip = addr[1]
        for i in range(0, len(GROUP)):
            if ip == LOCAL_IP:
                return
            elif i == len(GROUP) - 1:
                Agroup(ip, id)


def Listener():
    TCP = socket(AF_INET, SOCK_STREAM)
    TCP.bind((LOCAL_IP, PORT))
    print('Listening in', LOCAL_IP+':'+str(PORT))
    # Listening for connections
    TCP.listen(1)
    while RUNNING:
        conn, addr = TCP.accept()
        message = ReceiveMessage(conn)
        if not message: continue
        if message['Type'] == AGROUP or message['Type'] == INCLUDE:
            # Creating a new connection
            content = message['Content'].split()[0].split(':')
            id = int(content[1])
            ip = addr[0]
            for i in GROUP:
                if ip == GROUP[i]['IP']:
                    conn.close()
                    continue
            GROUP[id] = ip
            UpdateGroup(id, message['Content'])
            if message['Type'] == INCLUDE:
                ID = int(content[2])
        conn.close()
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
    total = len(GROUP)+1
    return key % total

def SetData(key, data):
    if not DHT:
        DATA[key] = data
    else:
        id = IdByKey(key)
        if ID == id:
            DATA[key] = data
        else:
            SendMessage(GROUP[id]['IP'], str(key)+':'+str(data), SET_DATA)

def GetData(key):
    id = IdByKey(key)
    if ID == id or not DHT:
        print('Data:', DATA[key])
    else:
        SendMessage(GROUP[id]['IP'], str(key), GET_DATA)

def GiveData(id, key):
    if key in DATA:
        SendMessage(GROUP[id]['IP'], str(DATA[key]), GIVE_DATA)
    else:
        SendMessage(GROUP[id]['IP'], str(NOT_FOUND), GIVE_DATA)

def ShowData():
    if not DATA:
        print('There aren\'t storaged data')
    for key, content in DATA.items():
        print(key, content)

# Starting communicator
listener = Thread(target=Listener)
listener.start()