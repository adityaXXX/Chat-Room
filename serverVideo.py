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
            Thread(target=ClientConnectionFrames, args=(client, )).start()
            Thread(target=ClientConnectionSound, args=(client, )).start()
        except:
            continue

def ClientConnectionSound(client):
    while True:
        data = b''
        # print("In client Connections...")
        try:
            data = client.recv(BufferSize).decode("utf-8")
            if data == "Sending Audio From Client":
                client.send(("Sending Sound From Client Confirmed"))
                data = client.recv(BufferSize)
                if not data:
                    break
                broadcastSound(client, data)
        except:
            continue
        break

def broadcastSound(clientSocket, data_to_be_sent):
    clientSocket.send(("Broadcasting Sound").encode("utf-8"))
    temp = clientSocket.recv(BufferSize).decode("utf-8")
    if temp == "Broadcast Sound":
        for client in addresses:
            if client != clientSocket:
                # print("Broadcasting...")
                client.sendall(data_to_be_sent)

def ClientConnectionFrames(client):
    while True:
        data = b''
        # print("In client Connections...")
        try:
            data = client.recv(BufferSize).decode("utf-8")
            if data == "Sending Frames From Client":
                while True:
                    client.send(("Sending Frames From Client Confirmed"))
                    data = client.recv(BufferSize)
                    if not data:
                        break
                    broadcastFrames(client, data)
        except:
            continue
        break

def broadcastFrames(clientSocket, data_to_be_sent):
    clientSocket.send(("Broadcasting Frames").encode("utf-8"))
    temp = clientSocket.recv(BufferSize).decode("utf-8")
    if temp == "Broadcast Frame":
        for client in addresses:
            if client != clientSocket:
                # print("Broadcasting...")
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
