from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import struct

# HOST = input("Enter Host IP\n")
HOST = '192.168.157.206'
PORT_AUDIO = 3000
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
ports = {'3000':True,'8000':True,'4000':False,'5000':False,'6000':False,'7000':False}

def ConnectionsUniv():
    while True:
        client, addr = serverUniv.accept()

        addresses[client] = addr
        print("{} is connected!!".format(addr))
        for port in ports:
            if ports[port] == False:
                client.sendall(port.encode())
                ports[port] = True

                client1,addr1 = server1.accept()
                client2,addr2 = server2.accept()
                client3,addr3 = server3.accept()
                client4,addr4 = server4.accept()

                if port == '4000':
                    Thread(target=ClientConnectionVideo, args=(port, client, client1,client2,client3,client4, )).start()
                if port == '5000':
                    Thread(target=ClientConnectionVideo, args=(port, client, client2,client1,client3,client4, )).start()
                if port == '6000':
                    Thread(target=ClientConnectionVideo, args=(port, client, client3,client1,client2,client4, )).start()
                if port == '7000':
                    Thread(target=ClientConnectionVideo, args=(port, client, client4,client1,client2,client4, )).start()
                break

def ConnectionsSound():
    while True:
        clientAudio, addr = serverAudio.accept()
        print("{} is connected!!".format(addr))
        addressesAudio[clientAudio] = addr[0]
        Thread(target=ClientConnectionSound, args=(clientAudio, )).start()


def ClientConnectionVideo(port, client, client1,client2,client3,client4):
    while True:
        if len(addresses)>1:
            lengthbuf = recvall(client1,client2,client3,client4, 4)
            length, = struct.unpack('!I', lengthbuf)
            STATUS  = recvall(client1,client2,client3,client4 , 6)
            STATUS = STATUS.decode()
            recvall(client1,client2,client3,client4, length-6)
            if STATUS == "INTIVE":
                del addresses[client]
                quitUsers[addresses[client][0]] = True
                ports[port] = False
                break


def ClientConnectionSound(clientAudio):
    while True:
        if quitUsers[addressesAudio[clientAudio]] == False:
            data = clientAudio.recv(BufferSize)
            broadcastSound(clientAudio, data)
        else:
            quitUsers[addressesAudio[clientAudio]] = False
            del addressesAudio[clientAudio]
            break


def recvall(client1,client2,client3,client4,BufferSize):
        databytes = b''
        i = 0
        while i != BufferSize:
            to_read = BufferSize - i
            if to_read > (1000 * CHUNK):
                databytes = client1.recv(1000 * CHUNK)
                i += len(databytes)
                broadcastVideo(client2,client3,client4, databytes)
            else:
                if BufferSize == 4 or BufferSize == 6:
                    databytes += client1.recv(to_read)
                else:
                    databytes = client1.recv(to_read)
                i += len(databytes)
                if BufferSize != 4 and BufferSize != 6:
                    broadcastVideo(client2,client3,client4, databytes)
        print("YES!!!!!!!!!" if i == BufferSize else "NO!!!!!!!!!!!!")
        if BufferSize == 4 or BufferSize == 6:
            broadcastVideo(client2,client3,client4, databytes)
            return databytes

def broadcastVideo(client2,client3,client4, data_to_be_sent):
        client2.sendall(data_to_be_sent)
        client3.sendall(data_to_be_sent)
        client4.sendall(data_to_be_sent)

def broadcastSound(clientSocket, data_to_be_sent):
    for clientAudio in addressesAudio:
        if clientAudio != clientSocket:
            clientAudio.sendall(data_to_be_sent)


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
print("Waiting for connection..")
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
