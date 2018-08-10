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
        Thread(target = ClientConnection, args=(client, )).start()

def ClientConnection(client):
    name = client.recv(BufferSize).decode("utf-8")
    client.send(("Hello {}".format(name)).encode("utf-8"))
    message = ("{} has joined the chat..").format(name)
    Broadcast(message.encode("utf-8"))
    clients[client] = name
    while True:
        msg = client.recv(BufferSize).decode("utf-8")
        if msg != "quit":
            Broadcast(msg.encode("utf-8"), name + ": ")
        else:
            message = ("{} has left the chat.").format(clients[client])
            Broadcast(message.encode("utf-8"))
            client.send(("Will see you soon..").encode("utf-8"))
            del clients[client]
            break

def Broadcast(msg, name = ""):
    for sockets in clients:
        sockets.send(name.encode("utf-8") + msg)

server = socket(family=AF_INET, type=SOCK_STREAM)
try:
    server.bind((HOST, PORT))
except OSError:
    print("Server Busy")
BufferSize = 1024

server.listen(5)
print("Waiting for Connections... ")
AcceptThread = Thread(target=Connections)
AcceptThread.start()
AcceptThread.join()
server.close()
