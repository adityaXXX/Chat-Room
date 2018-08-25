from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import struct

HOST = input("Enter Host IP\n")
PORT = 3000
lnF = 640*480*3
CHUNK = 1024
addresses = {}
threads = {}

def Connections():
    while True:
        try:
            client, addr = server.accept()
            print("{} is connected!!".format(addr))
            addresses[client] = addr
            if len(addresses) > 1:
                for sockets in addresses:
                    if sockets not in threads:
                        threads[sockets] = True
                        sockets.send(("start").encode())
                        Thread(target=ClientConnection, args=(sockets, )).start()
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

def broadcast(clientSocket, data_to_be_sent):
    for client in addresses:
        if client != clientSocket:
            client.sendall(data_to_be_sent)

def recvall(client, BufferSize):
        databytes = b''
        i = 0
        while i != BufferSize:
            to_read = BufferSize - i
            if to_read > (1000 * CHUNK):
                databytes = client.recv(1000 * CHUNK)
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
try:
    server.bind((HOST, PORT))
except OSError:
    print("Server Busy")

server.listen(2)
print("Waiting for connection..")
AcceptThread = Thread(target=Connections)
AcceptThread.start()
AcceptThread.join()
server.close()
