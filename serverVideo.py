from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import struct

HOST = "192.168.157.206"
PORT = 3000
lnF = 640*480*3
CHUNK = 1024
addresses = {}
addressesaudio = {}
threads = {}

def Connections():
    while True:
        try:
            client, addr = server.accept()
            clientaudio, addr1 = serveraudio.accept()
            print("{} is connected!! For video".format(addr))
            print("{} is connected!! For audio".format(addr1))
            addresses[client] = addr
            addressesaudio[client] = clientaudio
            if len(addresses) > 1:
                for sockets in addresses:
                    if sockets not in threads:
                        threads[sockets] = True
                        sockets.send(("start").encode())
                        Thread(target=ClientConnection, args=(sockets, )).start()
                        Thread(target=ClientConnectionAudio, args=(addressesaudio[sockets], )).start()
            else:
                continue
        except:
            continue

def ClientConnection(client):
    while True:
        try:
            lengthbuf = recvall(client, 4)
            length, = struct.unpack('!I', lengthbuf)
            recvall(client, length)
        except:
            continue

def ClientConnectionAudio(clientaudio):
    while True:
        try:
            recvall(clientaudio , 4096)
        except:
            continue


def broadcast(clientSocket, data_to_be_sent):
    for client in addresses:
        if client != clientSocket:
            client.sendall(data_to_be_sent)


def broadcastaudio(clientSocket, data_to_be_sent):
    for client in addressesaudio[client]:
        if client != clientSocket:
            client.sendall(data_to_be_sent)

def recvall(client, BufferSize):
        databytes = b''
        i = 0
        while i != BufferSize:
            to_read = BufferSize - i
            if to_read > (4 * CHUNK):
                databytes = client.recv(4 * CHUNK)
                i += len(databytes)
                broadcast(client, databytes)
            else:
                if BufferSize == 4:
                    databytes += client.recv(to_read)
                else:
                    databytes = client.recv(to_read)
                i += len(databytes)
                if BufferSize != 4:
                    broadcast(client, databytes)
        print("YES!!!!!!!!!" if i == BufferSize else "NO!!!!!!!!!!!!")
        if BufferSize == 4:
            broadcast(client, databytes)
            return databytes

server = socket(family=AF_INET, type=SOCK_STREAM)
serveraudio = socket(family=AF_INET, type=SOCK_STREAM)
try:
    server.bind((HOST, PORT))
    serveraudio.bind((HOST,PORT+1000))
except OSError:
    print("Server Busy")

server.listen(2)
serveraudio.listen(2)
print("Waiting for connection..")
AcceptThread = Thread(target=Connections)
AcceptThread.start()
AcceptThread.join()
server.close()
serveraudio.close()
