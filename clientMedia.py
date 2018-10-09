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

# HOST = input("Enter Server IP\n")
HOST = '192.168.157.206'
PORT_AUDIO = 3000
PORT1 = 4000
PORT2 = 5000
PORT3 = 6000
PORT4 = 7000
PORT_UNIV = 8000

BufferSize = 4096
CHUNK=1024
lnF = 640*480*3
FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100

ports = {'3000':True,'8000':True,'4000':False,'5000':False,'6000':False,'7000':False}
USERS = {}

def SendAudio():
    while True:
        if quit == False:
            data = stream.read(CHUNK)
            dataChunk = array('h', data)
            vol = max(dataChunk)
            if(vol > 500):
                print("Recording Sound...")
                clientAudioSocket.sendall(data)
            else:
                print("Silence..")
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
            jpg_as_text = zlib.compress(jpg_as_text, 9)
            if quit == False:
                databytes = b"ACTIVE" + IP.encode() +  jpg_as_text
            else:
                databytes = b"INTIVE" + IP.encode() + jpg_as_text
                print('Connection Terminated Mofo !!!')

            length = struct.pack('!I', len(databytes))
            bytesToBeSend = b''
            clientVideoSocket1.sendall(length)
            while len(databytes) > 0:
                if (5000 * CHUNK) <= len(databytes):
                    bytesToBeSend = databytes[:(5000 * CHUNK)]
                    databytes = databytes[(5000 * CHUNK):]
                    clientVideoSocket1.sendall(bytesToBeSend)
                else:
                    bytesToBeSend = databytes
                    clientVideoSocket1.sendall(bytesToBeSend)
                    databytes = b''
            print("##### Data Sent!! #####")
            if quit == True:
                break
        except:
            continue


def RecieveFrame(clientVideoSocket):
    while True:
        try:
            lengthbuf = recvallVideo(clientVideoSocket, 4)
            length, = struct.unpack('!I', lengthbuf)
            databytes = recvallVideo(clientVideoSocket, length)
            databytes1 = databytes
            STATUS = databytes[:6].decode()
            if STATUS == "ACTIVE" or STATUS == "INTIVE":
                ipUser = databytes[6:len(IP)+6].decode()
                databytes = databytes[(len(STATUS)+len(ipUser)):]
                img = zlib.decompress(databytes)
                # img = img[len(IP)+6:]

                if len(databytes1) == length:
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
                        background = cv2.resize(USERS[ipUser], (640, 480))
                        overlay = wvs.read()
                        overlay = cv2.resize(overlay, (200, 150))
                        s_img = overlay
                        finalImage = background
                        x_offset=440
                        y_offset=330
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
            else:
                continue
        except:
            continue


def recvallVideo(clientVideoSocket, size):
    databytes = b''
    while len(databytes) != size:
        to_read = size - len(databytes)
        if to_read > (5000 * CHUNK):
            databytes += clientVideoSocket.recv(5000 * CHUNK)
        else:
            databytes += clientVideoSocket.recv(to_read)
    return databytes

def get_ip_address():
    s = S.socket(S.AF_INET, S.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip =  s.getsockname()[0]
    return ip

clientVideoSocketUniv = socket(family=AF_INET, type=SOCK_STREAM)
clientVideoSocketUniv.connect((HOST, PORT_UNIV))

clientAudioSocket = socket(family=AF_INET, type=SOCK_STREAM)
clientAudioSocket.connect((HOST, PORT_AUDIO))

wvs = WebcamVideoStream(0).start()
PORTNUMBER = clientVideoSocketUniv.recv(4).decode()

clientVideoSocket1 = socket(family=AF_INET, type=SOCK_STREAM)
clientVideoSocket1.connect((HOST, PORTNUMBER))
ports[PORTNUMBER] = True
SendFrameThread = Thread(target=SendFrame).start()

for portnos in ports:
    if ports[portnos] == False:
        clientVideoSocket2 = socket(family=AF_INET, type=SOCK_STREAM)
        clientVideoSocket2.connect((HOST, portnos))
        ports[portnos] = True
        RecieveFrameThread = Thread(target=RecieveFrame, args=(clientVideoSocket2, )).start()
        break

for portnos in ports:
    if ports[portnos] == False:
        clientVideoSocket3 = socket(family=AF_INET, type=SOCK_STREAM)
        clientVideoSocket3.connect((HOST, portnos))
        ports[portnos] = True
        RecieveFrameThread = Thread(target=RecieveFrame, args=(clientVideoSocket3, )).start()
        break

for portnos in ports:
    if ports[portnos] == False:
        clientVideoSocket4 = socket(family=AF_INET, type=SOCK_STREAM)
        clientVideoSocket4.connect((HOST, portnos))
        ports[portnos] = True
        RecieveFrameThread = Thread(target=RecieveFrame, args=(clientVideoSocket4, )).start()
        break


audio=pyaudio.PyAudio()
stream=audio.open(format=FORMAT,channels=CHANNELS, rate=RATE, input=True, output = True,frames_per_buffer=CHUNK)

IP = get_ip_address()
quit = False

SendAudioThread = Thread(target=SendAudio).start()
RecieveAudioThread = Thread(target=RecieveAudio).start()
SendAudioThread.join()
