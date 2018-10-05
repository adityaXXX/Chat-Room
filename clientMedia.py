import cv2
import socket as S
from socket import socket, AF_INET, SOCK_STREAM
from imutils.video import WebcamVideoStream
import pyaudio
from array import array
from threading import Thread
import numpy as np
import zlib
import struct

HOST = input("Enter Server IP\n")
PORT_VIDEO = 4000
PORT_AUDIO = 5000

BufferSize = 4096
CHUNK=1024
lnF = 640*480*3
FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100

USERS = {}

def SendAudio():
    while True:
        if quit == False:
            data = stream.read(CHUNK)
            dataChunk = array('h', data)
            vol = max(dataChunk)
            if(vol > 500):
                print("Recording Sound...")
            else:
                print("Silence..")
                clientAudioSocket.sendall(data)
        else:
            break

def RecieveAudio():
    while True:
        if quit == False:
            data = recvallAudio(BufferSize)
            stream.write(data)
        else:
            break

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
            if quit == False:
                databytes ="ACTIVE" + IP +  databytes
            else:
                databytes ="INTIVE" + IP + databytes
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
            if quit == True:
                break
        except:
            continue


def RecieveFrame():
    while True:
        try:
            lengthbuf = recvallVideo(4)
            length, = struct.unpack('!I', lengthbuf)
            databytes = recvallVideo(length)
            img = zlib.decompress(databytes)
            STATUS = img[:6]
            ipUser = img[6:len(IP)+6]
            img = img[len(IP)+6:]

            if len(databytes) == length:
                print("Recieving Media..")
                print("Image Frame Size:- {}".format(len(img)))
                img = np.array(list(img))
                img = np.array(img, dtype = np.uint8).reshape(480, 640, 3)
                if ipUser not in USERS:
                    USERS[ipUser] = img
                else:
                    if STATUS == "ACTIVE":
                        USERS[ipUser] = img
                    else:
                        del USERS[ipUser]

                if len(USERS) == 1:
                    background = cv2.resize(USERS[ipUser], (1080, 720))
                    overlay = wvs.read()
                    overlay = cv2.resize(overlay, (200, 150))
                    s_img = overlay
                    finalImage = background
                    x_offset=880
                    y_offset=570
                    finalImage[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1]] = s_img

                elif len(USERS) == 2:
                    frames = []
                    for ip in USERS:
                        frames.append(USERS[ip])
                    l_img1 = cv2.resize(frames[0], (640, 480))
                    l_img2 = cv2.resize(frames[1], (640, 480))
                    overlay = wvs.read()
                    overlay = cv2.resize(overlay, (200, 150))
                    s_img = overlay
                    l_img = np.hstack((l_img1, l_img2))
                    finalImage = cv2.resize(l_img, (1280, 720))
                    x_offset = 1080
                    y_offset = 570
                    finalImage[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1]] = s_img

                elif len(USERS) == 3:
                    frames = []
                    for ip in USERS:
                        frames.append(USERS[ip])
                    l_img1 = cv2.resize(frames[0], (640, 480))
                    l_img2 = cv2.resize(frames[1], (640, 480))
                    l_img3 = cv2.resize(frames[2], (640, 480))
                    overlay = wvs.read()
                    overlay = cv2.resize(overlay, (640, 480))
                    s_img = overlay
                    l_img4 = np.hstack((l_img1, l_img2))
                    l_img5 = np.hstack((l_img3, s_img))
                    finalImage = np.vstack((l_img4, l_img5))
                    finalImage = cv2.resize(l_img, (1080, 720))
                    x_offset = 880
                    y_offset = 570
                    finalImage[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1]] = s_img


                cv2.imshow("Stream", finalImage)
                if cv2.waitKey(1) == 27:
                    quit = True
                    cv2.destroyAllWindows()
                    break
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

def get_ip_address():
    s = S.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip =  s.getsockname()[0]
    return ip

clientVideoSocket = socket(family=AF_INET, type=SOCK_STREAM)
clientVideoSocket.connect((HOST, PORT_VIDEO))
wvs = WebcamVideoStream(0).start()

clientAudioSocket = socket(family=AF_INET, type=SOCK_STREAM)
clientAudioSocket.connect((HOST, PORT_AUDIO))

audio=pyaudio.PyAudio()
stream=audio.open(format=FORMAT,channels=CHANNELS, rate=RATE, input=True, output = True,frames_per_buffer=CHUNK)

initiation = clientVideoSocket.recv(5).decode()

IP = get_ip_address()
quit = False

if initiation == "start":
    SendFrameThread = Thread(target=SendFrame).start()
    SendAudioThread = Thread(target=SendAudio).start()
    RecieveFrameThread = Thread(target=RecieveFrame).start()
    RecieveAudioThread = Thread(target=RecieveAudio).start()
