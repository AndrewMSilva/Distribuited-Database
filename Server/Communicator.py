from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
import hashlib
import random
import time
import json

# Main settings
LocalID      = 0
StandardPort = 5918
BufferLength = 1024
Running      = True
LocalIP      = None

# Group settings
Password = hashlib.sha1('Aa@215?'.encode('latin1')).hexdigest()
Group = {}

# Message types
Query       = 0
Agroup      = 1
UptadeGroup = 2

def BindSocket():
    # Getting local IP
    s = socket(AF_INET, SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        LocalIP = s.getsockname()[0]
    except:
        LocalIP = '127.0.0.1'
    finally:
            s.close()
    # Binding socket
    Group = {LocalID: LocalIP}
    TCP = socket(AF_INET, SOCK_STREAM)
    TCP.bind((LocalIP, StandardPort))
    print('Listening in', LocalIP+':'+str(StandardPort))
    return TCP

def EncodeMessage(type, content):
    message = {"Type": type, "Password": Password, "Time": time.time(), "Content": content}
    message = json.dumps(message)
    return message.encode('latin1')

def DecodeMessage(enconded_message):
    try:
        message = json.loads(enconded_message.decode('latin1'))
        if "Type" in message and "Password" in message and "Time" in message and "Content" in message:
            return message
        else:
            return False
    except:
        return False

def SendMessage(content, id, type):
    # Finding the destination
    if id in Group:
        enconded_message = EncodeMessage(type, content)
        try:
            tcp = socket(AF_INET, SOCK_STREAM)
            tcp.connect((ip, StandardPort))
            tcp.send(enconded_message)
            tcp.close()
        except Exception as e:
            print('Error:', e)
    else:
        print('ID not found!')

def ReceiveMessage(conn):
    enconded_message = conn.recv(BufferLength)
    message = DecodeMessage(enconded_message)
    # Verifying the message format
    if not message:
        conn.close()
        return False
    # Authenticating message
    elif message['Password'] != Password:
        print('Access denied: authentication falied')
        conn.close()
        return False
    # Interpreting message
    else:
        return message

''' Group methods '''

def Agroup(ip, id=None, type=Agroup):
    # Verifying the connection is itself
    if ip == LocalIP:
        print('Unable to connect to itself')
        return
    # Verifying if the connection already exists
    if ip in Group.values():
        print('IP already connected')
        return
    # Creating connection
    if SendAgroupMessage(ip, type):
        if not id:
            id = len(Group)
        
        Group[id] = ip
        print('Connected to', str(id)+':'+ip)


def SendAgroupMessage(ip, type=Agroup):
    content = str(LocalID) + ':' + str(len(Group))
    for i in Group:
        if Group[i] != LocalIP:
            content += ' ' + str(i) + ':' + Group[i]

    enconded_message = EncodeMessage(type, content)
    try:
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((ip, StandardPort))
        s.send(enconded_message)
        s.close()
        return True
    except Exception as e:
        print('Error:', e)
        return False

def Include(ip):
    Agroup(ip, type=Include)

def IncludeReceived(message):
    if message['Type'] == Agroup or message['Type'] == Include:
        # Verifying the new connection
        content = message['Content'].split()[0].split(':')
        id = int(content[0])
        ip = addr[0]
        for i in Group:
            if ip == Group[i]:
                conn.close()
                continue
        # Creating a new connection
        UpdateGroup(id, message['Content'])
        if message['Type'] == Include:
            print('Connected to', ip)
            old_id = LocalID
            del Group[old_id]
            LocalID = int(content[1])
            Group[LocalID] = LocalIP
            SendAgroupMessage(ip)
        Group[id] = ip

def ShowGroup():
    if not Group:
        print('There aren\'t connections')
    else:
        for i in sorted(Group.keys()):
            print('ID:', i, ' IP:', Group[i])

def UpdateGroup(id, content):
    content = content.split()[1:]
    for addr in content:
        addr = addr.split(':')
        id = addr[0]
        ip = addr[1]
        if not ip in Group.values():
            Agroup(ip, id)

def QuitGroup():
    for id in Group:
        if Group[id] != LocalID:
            SendMessage("None", id, QuitGroup)
            del Group[id]
    old_id = LocalID
    del Group[old_id]
    LocalID = 0
    Group[LocalID] = LocalIP
    SendAgroupMessage(ip)

''' DHT methods '''

StorageSpace = 256
Addresses    = [False]*StorageSpace

T = list(range(0, StorageSpace))
random.seed(StorageSpace)
random.shuffle(T)
# Pearson string hash
def GetPointer(file_name):
    h = [0]*StorageSpace
    n = len(file_name)
    for i in range(0, n):
        h[i+1] = T[h[i] ^ ord(file_name[i])]
    return h[n]

def GetIDByFileName(file_name):
    pointer = GetPointer(file_name)
    local_space = int(StorageSpace/len(Group))
    for id in sorted(Group.keys()):
        if pointer < local_space:
            break
        else:
            local_space += local_space
    print(id, pointer)
    return id

def FileExists(file_name):
    pointer = GetPointer(file_name)
    return Addresses[pointer]