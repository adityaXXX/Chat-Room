import cv2
from socket import socket, AF_INET, SOCK_STREAM
from imutils.video import WebcamVideoStream
from threading import Thread
import numpy as np
import zlib
import struct

HOST = input("Enter Server IP\n")
PORT = 3000

CHUNK=1024
lnF = 640*480*3

def SendFrame():
    while True:
        try:
            frame = wvs.read()
            cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 480))
            frame = np.array(frame, dtype = np.uint8).reshape(1, lnF)
            jpg_as_text = bytearray(frame)

            databytes = zlib.compress(jpg_as_text, 9)
            length = struct.pack('!I', len(databytes))
            bytesToBeSend = b''
            client.sendall(length)
            while len(databytes) > 0:
                if (1000 * CHUNK) <= len(databytes):
                    bytesToBeSend = databytes[:(1000 * CHUNK)]
                    databytes = databytes[(1000 * CHUNK):]
                    client.sendall(bytesToBeSend)
                else:
                    bytesToBeSend = databytes
                    client.sendall(bytesToBeSend)
                    databytes = b''
            print("##### Data Sent!! #####")
        except:
            continue

def RecieveMedia():
    while True:
        try:
            lengthbuf = recvall(4)
            length, = struct.unpack('!I', lengthbuf)
            databytes = recvall(length)
            img = zlib.decompress(databytes)
            if len(databytes) == length:
                print("Recieving Media..")
                print("Image Frame Size:- {}".format(len(img)))
                img = np.array(list(img))
                img = np.array(img, dtype = np.uint8).reshape(480, 640, 3)
                cv2.imshow("Stream", img)
                if cv2.waitKey(1) == 27:
                    cv2.destroyAllWindows()
            else:
                print("Data CORRUPTED")
        except:
            continue

def recvall(size):
    databytes = b''
    while len(databytes) != size:
        to_read = size - len(databytes)
        if to_read > (1000 * CHUNK):
            databytes += client.recv(1000 * CHUNK)
        else:
            databytes += client.recv(to_read)
    return databytes

client = socket(family=AF_INET, type=SOCK_STREAM)
client.connect((HOST, PORT))
wvs = WebcamVideoStream(0).start()

initiation = client.recv(5).decode()

if initiation == "start":
    RecieveFrameThread = Thread(target=RecieveMedia).start()
    SendFrameThread = Thread(target=SendFrame).start()
