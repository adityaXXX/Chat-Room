from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread


HOST = "192.168.157.206"
PORT = 3000
lnF = 640*480*3
CHUNK = 1024
BufferSize = lnF + 4*CHUNK + 3
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
            status = client.recv(6).decode()
            print (status {} .format(addresses[client]))
            if status == "INTIVE":
                del addresses[client]
                del threads[client]
                break
            elif status == "ACTIVE":
                data = client.recv(BufferSize)
                broadcast(client, data)
        except:
            continue

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
server.close()
