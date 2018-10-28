from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import struct

HOST = input("Enter Host IP\n")
# HOST = '172.16.84.73'
PORT_AUDIO = 10000
PORT1 = 4000
PORT2 = 5000
PORT3 = 6000
PORT4 = 7000
PORT_UNIV = 8000
lnF = 640*480*3
CHUNK = 1024
BufferSize = 4096
quitUsers = {}
addressesAudio = {}
addresses = {}
USERS = {'4000':[],'5000':[],'6000':[],'7000':[]}
ports = {'10000':True,'8000':True,'4000':False,'5000':False,'6000':False,'7000':False}

def accept(port, server1,server2,server3,server4):
    client1,addr1 = server1.accept()
    client2,addr2 = server2.accept()
    client3,addr3 = server3.accept()
    client4,addr4 = server4.accept()
    i = 0
    if port == '4000':
        PORTS = ['4000', '5000', '6000', '7000']
        print ("1st User detected")
    elif port == '5000':
        PORTS = ['5000', '4000', '6000', '7000']
        print ("2nd User detected")
    elif port == '6000':
        PORTS = ['6000', '4000', '5000', '7000']
        print ("3rd User detected")
    elif port == '7000':
        PORTS = ['7000', '4000', '5000', '6000']
        print ("4th User detected")
    clients = [client1, client2, client3, client4]
    for PORT in PORTS:
        if PORT != port:
            USERS[PORT].append(clients[i])
        i += 1
    return tuple(clients), PORTS

def ConnectionsUniv():
    while True:
        client, addr = serverUniv.accept()
        addresses[client] = addr
        quitUsers[addr[0]] = False
        print("{} is connected!!".format(addr))
        for port in sorted(ports.keys()):
            if ports[port] == False:
                client.sendall(port.encode())
                ports[port] = True

                if port == '4000':
                    clients, PORTS = accept(port, server1,server2,server3,server4)
                    Thread(target=ClientConnectionVideo, args=(port, client, clients, PORTS,)).start()
                if port == '5000':
                    clients, PORTS = accept(port, server2,server1,server3,server4)
                    Thread(target=ClientConnectionVideo, args=(port, client, clients, PORTS,)).start()
                if port == '6000':
                    clients, PORTS = accept(port, server3,server1,server2,server4)
                    Thread(target=ClientConnectionVideo, args=(port, client, clients, PORTS,)).start()
                if port == '7000':
                    clients, PORTS = accept(port, server4,server1,server2,server3)
                    Thread(target=ClientConnectionVideo, args=(port, client, clients, PORTS,)).start()
                break

def ConnectionsSound():
    while True:
        clientAudio, addr = serverAudio.accept()
        print("{} is connected!!".format(addr))
        addressesAudio[clientAudio] = addr[0]
        Thread(target=ClientConnectionSound, args=(clientAudio, )).start()


def ClientConnectionVideo(port, client, clients, PORTS):
    try:
        while True:
            if len(addresses)>1:
                databytes = b''
                client1 = clients[0]
                lengthbuf = recvall(port, client1, 4)
                databytes += lengthbuf
                length, = struct.unpack('!I', lengthbuf)
                STATUS  = recvall(port, client1, 6)
                databytes += STATUS
                STATUS = STATUS.decode()
                databytes += recvall(port, client1, length-6)
                broadcastVideo(port, databytes)
                if STATUS == "INTIVE":
                    i = 0
                    quitUsers[addresses[client][0]] = True
                    del addresses[client]
                    ports[port] = False
                    for PORT in PORTS:
                        if PORT != port:
                            # clients[i].shutdown(1)
                            # clients[i].close()
                            USERS[PORT].remove(clients[i])
                        i += 1
                    # client1.shutdown(1)
                    # client1.close()
                    # client.shutdown(1)
                    # client.close()
                    break
    except:
        ports[port] = False

def ClientConnectionSound(clientAudio):
    try:
        while True:
            if quitUsers[addressesAudio[clientAudio]] == False:
                data = clientAudio.recv(BufferSize)
                broadcastSound(clientAudio, data)
            else:
                quitUsers[addressesAudio[clientAudio]] = False
                del addressesAudio[clientAudio]
                break
    except:
        pass


def recvall(port, client1, BufferSize):
    databytes = b''
    i = 0
    while i != BufferSize:
        to_read = BufferSize - i
        if to_read > (1000 * CHUNK):
            databytes += client1.recv(1000 * CHUNK)
            i = len(databytes)
        else:
            databytes += client1.recv(to_read)
            i = len(databytes)
    return databytes

def broadcastVideoFrame(client, data_to_be_sent, port):
    try:
        client.sendall(data_to_be_sent)
    except:
        # ports[port] = False
        # USERS[port] = []
        pass


def broadcastVideo(port, data_to_be_sent):
    # threads = []
    for client in USERS[port]:
        frameThread = Thread(target=broadcastVideoFrame, args=(client, data_to_be_sent, port, ))
        frameThread.start()
        # threads.append(frameThread)
        frameThread.join()
    # for thread in threads:
        # thread.join()

def broadcastSound(clientSocket, data_to_be_sent):
    temp = addressesAudio.copy()
    for clientAudio in temp:
        if clientAudio != clientSocket:
            try:
                clientAudio.sendall(data_to_be_sent)
            except:
                pass


serverAudio = socket(family=AF_INET, type=SOCK_STREAM)
server1 = socket(family=AF_INET, type=SOCK_STREAM)
server2 = socket(family=AF_INET, type=SOCK_STREAM)
server3 = socket(family=AF_INET, type=SOCK_STREAM)
server4 = socket(family=AF_INET, type=SOCK_STREAM)
serverUniv = socket(family=AF_INET, type=SOCK_STREAM)
try:
    serverAudio.bind((HOST, PORT_AUDIO))
except OSError:
    print("Server Audio is Busy")

try:
    serverUniv.bind((HOST, PORT_UNIV))
except OSError:
    print("Server Univ Busy")

try:
    server1.bind((HOST, PORT1))
except OSError:
    print("Server1 Busy")

try:
    server2.bind((HOST, PORT2))
except OSError:
    print("Server2 Busy")

try:
    server3.bind((HOST, PORT3))
except OSError:
    print("Server3 Busy")

try:
    server4.bind((HOST, PORT4))
except OSError:
    print("Server4 Busy")

serverAudio.listen(4)
AcceptThreadAudio = Thread(target=ConnectionsSound)
AcceptThreadAudio.start()


serverUniv.listen(4)
server1.listen(4)
server2.listen(4)
server3.listen(4)
server4.listen(4)
print("Waiting for connection..")
AcceptThreadUniv = Thread(target=ConnectionsUniv)
AcceptThreadUniv.start()
AcceptThreadUniv.join()
serverUniv.close()
