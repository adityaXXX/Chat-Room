from socket import AF_INET, SOCK_STREAM, socket
from threading import Thread

HOST = input("Enter Host IP: ")
PORT = eval(input("Enter Port No: "))
BufferSize = 1024

def Recieve():
    while True:
        try:
            msg = client.recv(BufferSize).decode("utf-8")
            print(msg)
        except OSError:
            break

def Send():
    while True:
        msg = input()
        if msg == "quit":
            client.send(msg.encode("utf-8"))
            client.close()
            break
        else:
            client.send(msg.encode("utf-8"))

client = socket(family=AF_INET, type=SOCK_STREAM)
client.connect((HOST, PORT))

RecieveThread = Thread(target=Recieve).start()
SendThread = Thread(target=Send).start()
