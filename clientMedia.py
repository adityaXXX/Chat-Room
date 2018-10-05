import cv2
from socket import socket, AF_INET, SOCK_STREAM
from imutils.video import WebcamVideoStream
import pyaudio
from array import array
from threading import Thread
import numpy as np
import zlib
import struct

HOST = input("Enter Server IP\n")
PORT_VIDEO = 3000
PORT_AUDIO = 4000

BufferSize = 4096
CHUNK=1024
lnF = 640*480*3
FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100

def SendAudio():
    while True:
        data = stream.read(CHUNK)
        dataChunk = array('h', data)
        vol = max(dataChunk)
        if(vol > 500):
            print("Recording Sound...")
        else:
            print("Silence..")
        clientAudioSocket.sendall(data)

def RecieveAudio():
    while True:
        data = recvallAudio(BufferSize)
        stream.write(data)

def recvallAudio(size):
    databytes = b''
    while len(databytes) != size:
        to_read = size - len(databytes)
        if to_read > (4 * CHUNK):
            databytes += clientAudioSocket.recv(4 * CHUNK)
        else:
            databytes += clientAudioSocket.recv(to_read)
    return databytes

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
            clientVideoSocket.sendall(length)
            while len(databytes) > 0:
                if (5000 * CHUNK) <= len(databytes):
                    bytesToBeSend = databytes[:(5000 * CHUNK)]
                    databytes = databytes[(5000 * CHUNK):]
                    clientVideoSocket.sendall(bytesToBeSend)
                else:
                    bytesToBeSend = databytes
                    clientVideoSocket.sendall(bytesToBeSend)
                    databytes = b''
            print("##### Data Sent!! #####")
        except:
            continue


def RecieveFrame():
    while True:
        try:
            lengthbuf = recvallVideo(4)
            length, = struct.unpack('!I', lengthbuf)
            databytes = recvallVideo(length)
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


def recvallVideo(size):
    databytes = b''
    while len(databytes) != size:
        to_read = size - len(databytes)
        if to_read > (5000 * CHUNK):
            databytes += clientVideoSocket.recv(5000 * CHUNK)
        else:
            databytes += clientVideoSocket.recv(to_read)
    return databytes



clientVideoSocket = socket(family=AF_INET, type=SOCK_STREAM)
clientVideoSocket.connect((HOST, PORT_VIDEO))
wvs = WebcamVideoStream(0).start()

clientAudioSocket = socket(family=AF_INET, type=SOCK_STREAM)
clientAudioSocket.connect((HOST, PORT_AUDIO))

audio=pyaudio.PyAudio()
stream=audio.open(format=FORMAT,channels=CHANNELS, rate=RATE, input=True, output = True,frames_per_buffer=CHUNK)

initiation = clientVideoSocket.recv(5).decode()

if initiation == "start":
    SendFrameThread = Thread(target=SendFrame).start()
    SendAudioThread = Thread(target=SendAudio).start()
    RecieveFrameThread = Thread(target=RecieveFrame).start()
    RecieveAudioThread = Thread(target=RecieveAudio).start()
