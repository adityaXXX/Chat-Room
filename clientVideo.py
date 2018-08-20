import cv2
from socket import socket, AF_INET, SOCK_STREAM
from imutils.video import WebcamVideoStream
from threading import Thread
import numpy as np
import pyaudio
from array import array
import keyboard

HOST = "192.168.157.206"
PORT = 4000
BufferSize = 4096
lnF = 640*480*3

FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100
CHUNK=1024
lnS = 4096

waitIn = 0
waitOut = 0

def SendAudio():
    data = stream.read(CHUNK)
    dataChunk = array('h', data)
    vol = max(dataChunk)
    # if(vol > 500):
    print("Recording Sound...") ################# CHECK
    client.sendall(data)

def SendVideo():
    frame = wvs.read()
    cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = cv2.resize(cv2_im, (640, 480))
    frame = np.array(frame).reshape(1, ln)
    jpg_as_text = bytearray(frame)
    print("Sending Frames...")
    client.sendall(jpg_as_text)

def sending():
    print("In sending...")
    while True:
        print("Sending Video...")
        SendVideo()
        print("Sending Audio...")
        SendAudio()

def RecieveAudio():
    data = b''
    while True:
        to_read = lnS - len(data)
        if to_read > CHUNK:
            data += client.recv(CHUNK)
        else:
            data += client.recv(to_read)
            break
    stream.write(data)

def RecieveVideo():
    data = b''
    while True:
        to_read = lnF - len(data)
        if to_read > BufferSize:
            data += client.recv(BufferSize)
        else:
            data += client.recv(to_read)
            break
    img = list(data)
    img = np.array(img, dtype = np.uint8).reshape(480, 640, 3)
    cv_image = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    cv2.imshow("Stream", cv_image)

def recieving():
    print("In recieving...")
    while True:
        RecieveVideo()
        print ("########Recieved Video########")
        RecieveAudio()
        print ("############Recieved audio##########")


client = socket(family=AF_INET, type=SOCK_STREAM)
client.connect((HOST, PORT))

wvs = WebcamVideoStream(0).start()
audio=pyaudio.PyAudio()
stream=audio.open(format=FORMAT,channels=CHANNELS, rate=RATE, input=True, output = True, frames_per_buffer=CHUNK)

RecieveFrameThread = Thread(target=recieving).start()
SendFrameThread = Thread(target=sending).start()
