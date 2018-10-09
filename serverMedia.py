from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import struct

# HOST = input("Enter Host IP\n")
HOST = '192.168.157.206'
PORT_VIDEO = 3000
PORT_AUDIO = 4000
lnF = 640*480*3
CHUNK = 1024
BufferSize = 4096
addressesAudio = {}
addresses = {}
threads = {}

def ConnectionsVideo():
    while True:
        clientVideo, addr = serverVideo.accept()
        print("{} is connected!!".format(addr))
        addresses[clientVideo] = addr
        quitUsers[addresses[clientVideo][0]] = False
        if len(addresses) > 1:
            for sockets in list(addresses):
                if sockets not in threads:
                    threads[sockets] = True
                    sockets.send(("start").encode())
                    Thread(target=ClientConnectionVideo, args=(sockets, )).start()

        else:
            continue


def ConnectionsSound():
    while True:
        clientAudio, addr = serverAudio.accept()
        print("{} is connected!!".format(addr))
        addressesAudio[clientAudio] = addr[0]
        Thread(target=ClientConnectionSound, args=(clientAudio, )).start()


def ClientConnectionVideo(clientVideo):
    while True:
        lengthbuf = recvall(clientVideo, 4)
        length, = struct.unpack('!I', lengthbuf)
        STATUS  = recvall(clientVideo , 6)
        STATUS = STATUS.decode()
        recvall(clientVideo, length-6)
        if STATUS == "INTIVE":
            quitUsers[addresses[clientVideo][0]] = True
            del addresses[clientVideo]
            del threads[clientVideo]
            print(len(addresses))
            break


def ClientConnectionSound(clientAudio):
    while True:
        if quitUsers[addressesAudio[clientAudio]] == False:
            data = clientAudio.recv(BufferSize)
            broadcastSound(clientAudio, data)
        else:
            quitUsers[addresses[clientVideo][0]] = True
            break


def recvall(clientVideo, BufferSize):
        databytes = b''
        i = 0
        while i != BufferSize:
            to_read = BufferSize - i
            if to_read > (1000 * CHUNK):
                databytes = clientVideo.recv(1000 * CHUNK)
                i += len(databytes)
                broadcastVideo(clientVideo, databytes)
            else:
                if BufferSize == 4 or BufferSize == 6:
                    databytes += clientVideo.recv(to_read)
                else:
                    databytes = clientVideo.recv(to_read)
                i += len(databytes)
                if BufferSize != 4 and BufferSize != 6:
                    broadcastVideo(clientVideo, databytes)
        print("YES!!!!!!!!!" if i == BufferSize else "NO!!!!!!!!!!!!")
        if BufferSize == 4 or BufferSize == 6:
            broadcastVideo(clientVideo, databytes)
            return databytes

def broadcastVideo(clientSocket, data_to_be_sent):
    for clientVideo in list(addresses):
        if clientVideo != clientSocket:
            clientVideo.sendall(data_to_be_sent)

def broadcastSound(clientSocket, data_to_be_sent):
    for clientAudio in list(addressesAudio):
        if clientAudio != clientSocket:
            clientAudio.sendall(data_to_be_sent)

serverVideo = socket(family=AF_INET, type=SOCK_STREAM)
try:
    serverVideo.bind((HOST, PORT_VIDEO))
except OSError:
    print("Server Busy")

serverAudio = socket(family=AF_INET, type=SOCK_STREAM)
try:
    serverAudio.bind((HOST, PORT_AUDIO))
except OSError:
    print("Server Busy")

quitUsers = {}

serverAudio.listen(4)
print("Waiting for connection..")
AcceptThreadAudio = Thread(target=ConnectionsSound)
AcceptThreadAudio.start()


serverVideo.listen(4)
print("Waiting for connection..")
AcceptThreadVideo = Thread(target=ConnectionsVideo)
AcceptThreadVideo.start()
AcceptThreadVideo.join()
serverVideo.close()
