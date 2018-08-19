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
        # data = b''
        # print("In client Connections...")
        try:
            temp = client.recv(BufferSize).decode("utf-8")
            if temp == "Sending Audio From Client":
                client.send(("Sending Audio From Client Confirmed").encode("utf-8"))
                print("Audio Handshaking")
                data = client.recv(BufferSize)
                print("Recieved Audio")
                if not data:
                    break
                print("Audio sending")
                broadcast(client, "SOUND", data)
            if temp == "Sending Video From Client":
                client.send(("Sending Video From Client Confirmed").encode("utf-8"))
                print("Video Handshaking")
                data = client.recv(BufferSize)
                print("Recieved Video")
                if not data:
                    break
                print("Video sending")
                broadcast(client, "VIDEO", data)
            # print(data)
        except:
            continue
        break

def broadcast(clientSocket, format, data_to_be_sent):
    print("Broadcasting..")

    if format == "SOUND":
        for client in addresses:
            if client != clientSocket:
                while True:
                    client.send(("Broadcasting Sound").encode("utf-8"))
                    temp = client.recv(BufferSize).decode("utf-8")
                    if temp == "Broadcast Sound":
                        client.sendall(data_to_be_sent)
                        client.send(("Broadcasted").encode("utf-8"))
                        print("Broadcasted")
                        break

    elif format == "VIDEO":
        for client in addresses:
            if client != clientSocket:
                while True:
                    client.send(("Broadcasting Video").encode("utf-8"))
                    temp = client.recv(BufferSize).decode("utf-8")
                    if temp == "Broadcast Video":
                        client.sendall(data_to_be_sent)
                        print("Broadcasted")
                        break


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
