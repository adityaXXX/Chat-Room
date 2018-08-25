from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread


HOST = input("Enter Host IP\n")
PORT = 4000
BufferSize = 4096
addresses = {}

def Connections():
    while True:
        try:
            client, addr = server.accept()
            print("{} is connected!!".format(addr))
            addresses[client] = addr
            Thread(target=ClientConnectionSound, args=(client, )).start()
        except:
            continue

def ClientConnectionSound(client):
    while True:
        try:
            data = client.recv(BufferSize)
            broadcastSound(client, data)
        except:
            continue

def broadcastSound(clientSocket, data_to_be_sent):
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
