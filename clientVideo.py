import cv2
from socket import socket, AF_INET, SOCK_STREAM
from imutils.video import WebcamVideoStream
from threading import Thread
import numpy as np
import pyaudio
from array import array

HOST = "192.168.157.206"
PORT = 4000
BufferSize = 4096

FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100
CHUNK=1024
ln = 640*480*3 + 4*CHUNK + 3

def SendMedia():
    while True:
        try:
            frame = wvs.read()
            cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(cv2_im, (640, 480))
            frame = np.array(frame).reshape(1, lnF)
            jpg_as_text = bytearray(frame)

            data = stream.read(CHUNK)
            dataChunk = array('h', data)
            vol = max(dataChunk)
            if(vol > 500):
                print("Recording Sound...")
            databytes = jpg_as_text + b'xXx' + data
            print("Sending Media...")
            client.sendall(databytes)
        except:
            continue

def RecieveMedia():
    while True:
        try:
            databytes = client.recv(ln)
            img, data = databytes.split(b'xXx')
            img = list(img)
            img = np.array(img, dtype = np.uint8).reshape(480, 640, 3)
            cv_image = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            cv2.imshow("Stream", cv_image)
            cv2.waitKey(1)
            stream.write(data)
        except:
            continue

client = socket(family=AF_INET, type=SOCK_STREAM)
client.connect((HOST, PORT))

wvs = WebcamVideoStream(0).start()
audio=pyaudio.PyAudio()
stream=audio.open(format=FORMAT,channels=CHANNELS, rate=RATE, input=True, output = True, frames_per_buffer=CHUNK)

RecieveFrameThread = Thread(target=RecieveMedia).start()
SendFrameThread = Thread(target=SendMedia).start()
