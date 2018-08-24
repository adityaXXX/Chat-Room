import cv2
from socket import socket, AF_INET, SOCK_STREAM
from imutils.video import WebcamVideoStream
from threading import Thread
import numpy as np
import pyaudio
from array import array
import zlib
import struct

HOST = "192.168.157.206"
PORT = 3000

FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100
CHUNK=1024
lnF = 640*480*3


def SendMedia():
    while True:
        try:
            frame = wvs.read()
            cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 480))
            frame = np.array(frame).reshape(1, lnF)
            jpg_as_text = bytearray(frame)
            databytes = zlib.compress(jpg_as_text, 9)
            length = struct.pack('!I', len(databytes))
            bytesToBeSend = b''
            client.sendall(length)
            while len(databytes) > 0:
                if (4 * CHUNK) <= len(databytes):
                    bytesToBeSend = databytes[:(4 * CHUNK)]
                    databytes = databytes[(4 * CHUNK):]
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
            lengthbuf = recvall(client , 4)
            length, = struct.unpack('!I', lengthbuf)
            databytes = recvall(client , length)
            databytes = zlib.decompress(databytes)
            print("Image Frame Size:- {}, Sound Frame Size:- {}".format(len(img), len(data)))
            if len(databytes) == lnF:
                print("Recieving Media..")
                img = list(img)
                img = np.array(img, dtype = np.uint8).reshape(480, 640, 3)
                cv2.imshow("Stream", img)
                if cv2.waitKey(1) == 27:
                    active = False
                    cv2.destroyAllWindows()
            else:
                print("Data CORRUPTED")
        except:
            continue

def SendSoundMedia():
    while True:
        data = stream.read(CHUNK)
        dataChunk = array('h', data)
        vol = max(dataChunk)
        if(vol > 500):
            print("Recording Sound...")
        clientaudio.sendall(data)

def RecieveSoundMedia():
    while True:
        try:
            sound = recvall(clientaudio , 4096)
            stream.write(sound)
        except:
            continue

def recvall(client , size):
    databytes = b''
    while len(databytes) != size:
        to_read = size - len(databytes)
        if to_read > (4 * CHUNK):
            databytes += client.recv(4 * CHUNK)
        else:
            databytes += client.recv(to_read)
    return databytes

client = socket(family=AF_INET, type=SOCK_STREAM)
client.connect((HOST, PORT))

clientaudio = socket(family=AF_INET, type=SOCK_STREAM)
clientaudio.connect((HOST, PORT+1000))

wvs = WebcamVideoStream(0).start()
audio=pyaudio.PyAudio()
stream=audio.open(format=FORMAT,channels=CHANNELS, rate=RATE, input=True, output = True, frames_per_buffer=CHUNK)

initiation = client.recv(5).decode()
active = True
if initiation == "start":
    RecieveFrameThread = Thread(target=RecieveMedia).start()
    SendFrameThread = Thread(target=SendMedia).start()
    RecieveSoundThread = Thread(target=RecieveSoundMedia).start()
    SendSoundThread = Thread(target=SendSoundMedia).start()
