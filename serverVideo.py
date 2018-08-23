from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread


HOST = "192.168.43.215"
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
            # status = client.recv(6).decode() ################ INCLUDE THIS TOO
            # print ("status:- {} ".format(status))
            # if status == "INTIVE":
            #     del addresses[client]
            #     del threads[client]
            #     break
            # elif status == "ACTIVE":
            databytes = b''
            i = 0
            while i != BufferSize:
                to_read = BufferSize - i
                if to_read > (4 * CHUNK):
                    databytes = client.recv(4 * CHUNK)
                    i += len(databytes)
                    broadcast(client, databytes)
                else:
                    databytes = client.recv(to_read)
                    i += len(databytes)
                    broadcast(databytes)
            print("YES!!!!!!!!!" if i == BufferSize else "NO!!!!!!!!!!!!")
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
