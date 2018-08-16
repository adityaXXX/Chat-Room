from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread

import numpy as np

HOST = "192.168.43.215"
PORT = 5000
BufferSize = 4096
addresses = {}

def Connections():
    while True:
        client, addr = server.accept()
        print("{} is connected!!".format(addr))
        # client.send(("Welcome to Chat Room. Press {q} to exit").encode("utf-8"))
        addresses[client] = addr
        Thread(target=ClientConnection, args=(client, )).start()

def ClientConnection(client):
    length = int(client.recv(2 * BufferSize).decode("utf-8"))
    SendLength(client, str(length))
    while True:
        # print("In client Connections...")
        receivingBuffer = client.recv(BufferSize)
        if not receivingBuffer:
            break
        data = b''
        if len(data) < length:

            to_read = length - len(data)
            data = client.recv(BufferSize if to_read > BufferSize else to_read)
            length -= len(data)
        broadcast(client, data)

def SendLength(clientSocket, length):
    for client in addresses:
        if client != clientSocket:
            print("sending length:- {}".format(len(length)))
            client.send(length.encode("utf-8"))


def broadcast(clientSocket, receivingBuffer):
    for client in addresses:
        if client != clientSocket:
            # print("Broadcasting...")
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
