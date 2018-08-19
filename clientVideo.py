import cv2
from socket import socket, AF_INET, SOCK_STREAM
from imutils.video import WebcamVideoStream
from threading import Thread
import numpy as np
import pyaudio
import keyboard

HOST = "192.168.157.206"
PORT = 4000
BufferSize = 4096
ln = 640*480*3

FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100
CHUNK=1024

waitIn = 0
waitOut = 0

def SendAudio():
    try:
        data = stream.read(CHUNK)
        dataChunk = array('h', data)
        vol = max(dataChunk)
        if(vol > 500):
            print("Recording Sound...")
            client.send(data)
    except:
        continue

def RecieveAudio():
    try:
        data = client.recv(BufferSize)
        stream.write(data)
    except:
        continue

def RecieveVideo():
    try:
        data = b''
        while True:
            to_read = ln - len(data)
            if to_read > BufferSize:
                data += client.recv(BufferSize)
            else:
                data += client.recv(to_read)
                break
        img = list(data)
        img = np.array(img, dtype = np.uint8).reshape(480, 640, 3)
        cv_image = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        cv2.imshow("Stream", cv_image)
    except:
        continue
def SendVideo():
    try:
        frame = wvs.read()
        cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(cv2_im, (640, 480))
        frame = np.array(frame).reshape(1, ln)
        jpg_as_text = bytearray(frame)
        client.sendall(jpg_as_text)
##            print("Client is sending Frames...")
##                client.send(b'')
    except:
        continue

def sending():
    print('Sending Video and Audio feed...')
    while True:
        try:
            client.send(("Sending Audio From Client").encode())
            flag = client.recv(BufferSize).decode()
            if flag == "Sending Audio From Client Confirmed":
                SendAudio()
            client.send(("Sending Video From Client").encode())
            flag = client.recv(BufferSize).decode()
            if flag == "Sending Video From Client Confirmed":
                SendVideo()
            if keyboard.is_pressed('q'):
##                    waitOut == 1
                    break

def recieving():
    print('Recieving Video and Audio feed...')
    while True:
        try:
            flag = client.recv(BufferSize).decode()
            if flag == "Broadcasting Sound":
                client.send(("Broadcast Sound").encode())
                RecieveAudio()
            flag = client.recv(BufferSize).decode()
            if flag == "Broadcasting Video":
                client.send(("Broadcast Video").encode())
                RecieveVideo()
            if keyboard.is_pressed('q'):
##                    waitOut == 1
                    break

client = socket(family=AF_INET, type=SOCK_STREAM)
client.connect((HOST, PORT))
wvs = WebcamVideoStream(0).start()
audio=pyaudio.PyAudio()
stream=audio.open(format=FORMAT,channels=CHANNELS, rate=RATE, input=True, output = True, frames_per_buffer=CHUNK)
RecieveFrameThread = Thread(target=recieving).start()
SendFrameThread = Thread(target=sending).start()
##RecieveAudioThread = Thread(target=RecieveAudio).start()
##SendAudioThread = Thread(target=SendAudio).start()
