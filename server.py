from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread

HOST = "127.0.0.1"
PORT = 3000

addresses = {}
clients = {}

def Connections():
    while True:
        client, addr = server.accept()
        print("{} is connected!!".format(addr))
        client.send(("Welcome to Chat Room. Type {quit} to exit. Enter your name: ").encode("utf-8"))
        addresses[client] = addr
        Thread(target = ClientConnection, args=(client)).start()

def ClientConnection(client):
    name = client.recv(BufferSize).decode("utf-8")
    client.send(("Hello {}".format(name)).encode("utf-8"))
    Broadcast(("{} has joined the chat..").format(name))
    clients[client] = name
    while True:
        msg = client.recv(BufferSize).decode("utf-8")
        if msg != quit:
            Broadcast(msg, name + ": ")
        else:
            Broadcast(("{} has left the chat.").format(client[client]))
            client.send(("Will see you soon..").encode("utf-8"))
            del clients[client]
            break

def Broadcast(msg, name = ""):
    for sockets in clients:
        socket.send((name + msg).encode("utf-8"))

server = socket(family=AF_INET, type=SOCK_STREAM)
socket.bind((HOST, PORT))
BufferSize = 1024

server.listen(5)
print("Waiting for Connections... ")
AcceptThread = Thread(target=Connections)
AcceptThread.start()
AcceptThread.join()
server.close()
