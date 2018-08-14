from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

import numpy as np

HOST = "192.168.157.206"
PORT = 3000
BufferSize = 4096
addresses = {}

def Connections():
    while True:
        client, addr = server.accept()
        print("{} is connected!!".format(addr))
        client.send(("Welcome to Chat Room. Press {q} to exit").encode("utf-8"))
        addresses[client] = addr
        Thread(target=ClientConnection, args=(client, )).start()

def ClientConnection(client):
    length = int(client.recv(8192).decode("utf-8"))
    SendLength(client, str(length))
    while True:
        receivingBuffer = client.recv(BufferSize)
        if not receivingBuffer:
            break
        data = b''
        if len(data) < length:
            data = client.recv(4096 if to_read > 4096 else to_read)
            to_read = length - len(data)
            length -= len(data)
        broadcast(client, data)

def SendLength(clientSocket, length):
    for client in addresses:
        if client != clientSocket:
            client.send(length.encode("utf-8"))


def broadcast(clientSocket, receivingBuffer):
    for client in addresses:
        if client != clientSocket:
            client.send(receivingBuffer)

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
