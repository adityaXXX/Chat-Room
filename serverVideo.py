from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread


HOST = "192.168.157.206"
PORT = 4000
BufferSize = 4096
addresses = {}

def Connections():
    while True:
        try:
            client, addr = server.accept()
            print("{} is connected!!".format(addr))
            addresses[client] = addr
            Thread(target=ClientConnection, args=(client, )).start()
        except:
            continue

def ClientConnection(client):
    while True:
        data = client.recv(BufferSize)
        broadcast(client, data)

def broadcast(clientSocket, data_to_be_sent):
    for client in addresses:
        if client != clientSocket:
            client.sendall(data_to_be_sent)


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
