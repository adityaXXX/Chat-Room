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

FORMAT=pyaudio.paInt8
CHANNELS=1
RATE=44100
CHUNK=1024
lnF = 640*480*3

sound = b''

def SendSound():
    global sound
    while True:
        sound += stream.read(CHUNK)
        dataChunk = array('h', data)
        vol = max(dataChunk)
        if(vol > 500):
            print("Recording Sound...")

def SendFrame():
    global sound
    while True:
        try:
            frame = wvs.read()
            cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (640, 480))
            frame = np.array(frame, dtype = np.uint8).reshape(1, lnF)
            jpg_as_text = bytearray(frame)

            databytes = zlib.compress(jpg_as_text, 9) + b'SPLIT' +  zlib.compress(sound, 9)
            sound = b''
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
            img, data = databytes.split(b'SPLIT')
            img, data = zlib.decompress(img), zlib.decompress(data)
            if len(databytes) == length:
                stream.write(data)
                print("Recieving Media..")
                img = np.array(list(img))
                img = np.array(img, dtype = np.uint8).reshape(480, 640, 3)
                print("Image Frame Size:- {}, Sound Frame Size:- {}".format(len(img), len(data)))
                cv2.imshow("Stream", img)
                if cv2.waitKey(1) == 27:
                    active = False
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
audio=pyaudio.PyAudio()
stream=audio.open(format=FORMAT,channels=CHANNELS, rate=RATE, input=True, output = True, frames_per_buffer=CHUNK)

initiation = client.recv(5).decode()
active = True
if initiation == "start":
    RecieveFrameThread = Thread(target=RecieveMedia).start()
    SendFrameThread = Thread(target=SendFrame).start()
    SendSoundThread = Thread(target=SendSound).start()
