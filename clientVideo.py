import cv2
from socket import socket, AF_INET, SOCK_STREAM
from imutils.video import WebcamVideoStream
from threading import Thread
import numpy as np
import pyaudio
import keyboard


HOST = "192.168.157.254"
PORT = 4000
BufferSize = 4096
ln = 640*480*3

FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100
CHUNK=1024

waitIn = 0
waitOut = 0
def RecieveFrames():
    # print("Client is recieving...")
        while True:
            temp = client.recv(BufferSize).decode("utf-8")
            if temp == "Broadcasting Frames":
                temp = client.send(("Broadcast Frame").encode("utf-8"))
                try:
                    data = b''
                    while True:
                        to_read = ln - len(data)
                        if to_read > BufferSize:
                            data += client.recv(BufferSize)
                        else:
                            data += client.recv(to_read)
                            break

                    print("Recieved Frame...")
                    img = list(data)
                    img = np.array(img, dtype = np.uint8).reshape(480, 640, 3)
                    print("Img:- {}".format(img))
                    cv_image = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                    cv2.imshow("Stream", cv_image)
                    if cv2.waitKey(1) == 27:
                        waitIn = 1
                        break
                except:
                    continue


def SendFrames():
    wvs = WebcamVideoStream(0).start()
    client.send(("Sending Frames From Client").encode("utf-8"))
    while True:
        try:
            data = client.recv(BufferSize).decode("utf-8")
            frame = wvs.read()
            cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(cv2_im, (640, 480))
            frame = np.array(frame).reshape(1, ln)
            jpg_as_text = bytearray(frame)
            if data == "Sending Frames From Client Confirmed":
                client.sendall(jpg_as_text)
                print("Client is sending Frames...")
                if keyboard.is_pressed('q'):
                    waitOut == 1
                    break
        except:
            continue
    client.send(b'')

def SendAudio():
    while(waitOut == 0):
        client.send(("Sending Audio From Client").encode("utf-8"))
        try:
            temp = client.recv(BufferSize).decode("utf-8")
            data = stream.read(CHUNK)
            dataChunk = array('h', data)
            vol = max(dataChunk)
            if temp == "Sending Sound From Client Confirmed":
                if(vol > 500):
                    print("Recording Sound...")
                    client.send(data)
        except:
            continue
    client.send(b'')

def RecieveAudio():
    while(waitOut == 0):
        try:
            temp = client.recv(BufferSize).decode("utf-8")
            if temp == "Broadcasting Sound":
                client.send("Broadcast Sound")
                data = client.recv(BufferSize)
                stream.write(data)
        except:
            continue


client = socket(family=AF_INET, type=SOCK_STREAM)
client.connect((HOST, PORT))

audio=pyaudio.PyAudio()
stream=audio.open(format=FORMAT,channels=CHANNELS, rate=RATE, input=True, output = True, frames_per_buffer=CHUNK)

RecieveFrameThread = Thread(target=RecieveFrames).start()
SendFrameThread = Thread(target=SendFrames).start()
RecieveAudioThread = Thread(target=RecieveAudio).start()
SendAudioThread = Thread(target=SendAudio).start()
