from flask import Flask, render_template, Response, request
# import os
# import random
import cv2
import socket as S
from socket import socket, AF_INET, SOCK_STREAM
from webcamVideoStream import WebcamVideoStream
import pyaudio
from threading import Thread
import numpy as np
import zlib
import struct

# HOST = input("Enter Server IP\n")
HOST = '172.16.84.167'
PORT_AUDIO = 10000
PORT1 = 4000
PORT2 = 5000
PORT3 = 6000
PORT4 = 7000
PORT_UNIV = 8000

BufferSize = 4096
CHUNK=1024
lnF = 200*200*3
FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100

ports = {'10000':True,'8000':True,'4000':False,'5000':False,'6000':False,'7000':False}
USERS = {}
imageStream = np.array([])
quit1=False
startaudio = 1
startvideo = 1
app = Flask(__name__)

@app.route('/')
def home():
    #os.system("python3 script.py")
    ip_addr = get_ip_address()
    return render_template('home.html',ip_addr=ip_addr)

@app.route('/hosted')
def hosting():
    global HOST
    ip_addr = get_ip_address()
    HOST = ip_addr
    ServerThread = Thread(target = ServerMedia , args= ()) #####################CHAnge ServerMEdia File##########################
    ServerThread.start()
    return render_template('index.html')

@app.route('/connectfeed',methods=['POST'])
def connectfeed():
    global HOST
    ip_addr = request.form['inputval']
    HOST = ip_addr
    return render_template("index.html")

def RecieveFrame(clientVideoSocket):
    IP = get_ip_address()
    global quit1
    global imageStream
    while True:
        q = quit1
        lengthbuf = recvallVideo(clientVideoSocket, 4)
        # print('Lengthbuf - ',lengthbuf)
        length, = struct.unpack('!I', lengthbuf)
        # print('Length - ',length)
        databytes = recvallVideo(clientVideoSocket, length)
        databytes1 = databytes
        # print('Status - ',databytes[:6])
        STATUS = databytes[:6].decode()
        if STATUS == "ACTIVE" or STATUS == "INTIVE":
            lenip, = struct.unpack('!I',databytes[6:10])
            ipUser = databytes[10:10+int(lenip)]
            databytes = databytes[(len(STATUS)+4+len(ipUser)):]
            img = zlib.decompress(databytes)
            if len(databytes1) == length:
                # print("Recieving Media..")
                # print("Image Frame Size:- {}".format(len(img)))
                img = np.array(list(img))##NOT THERE
                img = np.array(img, dtype = np.uint8).reshape(200, 200, 3)##NOT THERE
                if ipUser not in USERS:
                    USERS[ipUser] = img
                else:
                    if STATUS == "ACTIVE":
                        USERS[ipUser] = img
                    elif STATUS == "INTIVE":
                        del USERS[ipUser]
            else:
                print("Data CORRUPTED")
        if q==True:
            clientVideoSocket.shutdown(1)
            clientVideoSocket.close()
            break #######CHANGED######

@app.route('/video_feed')
def video_feed():
    clientVideoSocketUniv = socket(family=AF_INET, type=SOCK_STREAM)
    clientVideoSocketUniv.connect((HOST, PORT_UNIV))

    wvs = WebcamVideoStream(0).start()

    clientAudioSocket = socket(family=AF_INET, type=SOCK_STREAM)
    clientAudioSocket.connect((HOST, PORT_AUDIO))

    PORTNUMBER = clientVideoSocketUniv.recv(4).decode()

    clientVideoSocket1 = socket(family=AF_INET, type=SOCK_STREAM)
    clientVideoSocket1.connect((HOST, int(PORTNUMBER)))
    ports[PORTNUMBER] = True

    for portnos in sorted(ports.keys()):
        if ports[portnos] == False:
            clientVideoSocket2 = socket(family=AF_INET, type=SOCK_STREAM)
            clientVideoSocket2.connect((HOST, int(portnos)))
            ports[portnos] = True
            RecieveFrameThread1 = Thread(target=RecieveFrame , args = (clientVideoSocket2,)).start()
            print(portnos,' - Connected !')
            break

    for portnos in sorted(ports.keys()):
        if ports[portnos] == False:
            clientVideoSocket3 = socket(family=AF_INET, type=SOCK_STREAM)
            clientVideoSocket3.connect((HOST, int(portnos)))
            ports[portnos] = True
            RecieveFrameThread2 = Thread(target=RecieveFrame , args = (clientVideoSocket3,)).start()
            print(portnos,' - Connected !')
            break

    for portnos in sorted(ports.keys()):
        if ports[portnos] == False:
            clientVideoSocket4 = socket(family=AF_INET, type=SOCK_STREAM)
            clientVideoSocket4.connect((HOST, int(portnos)))
            ports[portnos] = True
            RecieveFrameThread3 = Thread(target=RecieveFrame , args = (clientVideoSocket4,)).start()
            print(portnos,' - Connected !')
            break

    audio=pyaudio.PyAudio()
    stream=audio.open(format=FORMAT,channels=CHANNELS, rate=RATE, input=True, output = True,frames_per_buffer=CHUNK)

    closethread = Thread(target = initialize , args = (clientVideoSocketUniv,))
    closethread.start()

    SendAudioThread = Thread(target=SendAudio , args=(clientAudioSocket , stream ,))
    RecieveAudioThread = Thread(target=RecieveAudio , args=(clientAudioSocket , stream ,))
    # DisplayThread = Thread(target=display) #############         TRY          ######################
    # RecieveAudioThread.start()
    # DisplayThread.start()
    # SendAudioThread.start()
    SendFrameThread = Thread(target=SendFrame , args=(clientVideoSocket1 , wvs)).start()
    return Response(gen(wvs),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    # SendAudioThread.join()
    closethread.join()

def initialize(clientVideoSocketUniv):
    global quit1
    while True:
        q = quit1
        if q == True:
            clientVideoSocketUniv.shutdown(1)
            clientVideoSocketUniv.close()
            break
        else:
            pass

def gen(wvs):
    global quit1
    global USERS
    while True:
        US = USERS.copy()
        if len(US) == 1:
            for user in US:
                overlay = wvs.read()
                overlay = cv2.resize(overlay, (200, 150))
                s_img = overlay
                finalImage = cv2.resize(US[user],(1080,600))
                x_offset=880
                y_offset=450
                finalImage[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1]] = s_img
                ret, frame = cv2.imencode('.jpg', finalImage)
                finalImage = frame.tobytes()

        elif len(US) == 2:
            frames = []
            for ip in US:
                frames.append(USERS[ip])
            overlay = wvs.read()
            overlay = cv2.resize(overlay, (200, 150))
            s_img = overlay
            l_img = np.hstack((frames[0] , frames[1]))
            finalImage = cv2.resize(l_img, (1080, 600))
            x_offset = 880
            y_offset = 450
            finalImage[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1]] = s_img
            ret, frame = cv2.imencode('.jpg', finalImage)
            finalImage = frame.tobytes()

        elif len(US) == 3:
            frames = []
            for ip in US:
                frames.append(USERS[ip])
            overlay = wvs.read()
            overlay = cv2.resize(overlay, (200, 200))
            s_img = overlay
            l_img4 = np.hstack((frames[0] , frames[1]))
            l_img5 = np.hstack((frames[2], s_img))
            finalImage = np.vstack((l_img4, l_img5))
            finalImage = cv2.resize(finalImage, (1080, 600))
            ret, frame = cv2.imencode('.jpg', finalImage)
            finalImage = frame.tobytes()

        elif len(US) == 0:
            finalImage = wvs.read()
            finalImage = cv2.resize(finalImage, (1080, 600))
            ret, frame = cv2.imencode('.jpg', finalImage)
            finalImage = frame.tobytes()

        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + finalImage + b'\r\n\r\n') #########DOUBT#####CANT BE CHANGED########

def SendAudio(clientAudioSocket , stream):
    global quit1
    while True:
        q = quit1
        if q == False:
            if startaudio == 1:
                data = stream.read(CHUNK)
                clientAudioSocket.sendall(data)
        else:
            clientAudioSocket.shutdown(1)
            clientAudioSocket.close()
            break  ####CHANGED####

def RecieveAudio(clientAudioSocket , stream):
    global quit1
    while True:
        q = quit1
        if q == False:
            data = recvallAudio(clientAudioSocket, BufferSize)
            stream.write(data)
        else:
            break ######CHANGED#######

def recvallAudio(clientAudioSocket,size):
    databytes = b''
    while len(databytes) != size:
        to_read = size - len(databytes)
        if to_read > (4 * CHUNK):
            databytes += clientAudioSocket.recv(4 * CHUNK)
        else:
            databytes += clientAudioSocket.recv(to_read)
    return databytes ##########CHANGED######

@app.route('/audio')
def listen():
    global startaudio
    if startaudio == 0:
        startaudio = 1
    else:
        startaudio = 0
    print("Audio success")
    return "jbsdj"

def SendFrame(clientVideoSocket1 , wvs):
    IP = get_ip_address()
    global quit1
    while True:
        q = quit1
        if startvideo == 1:
            frame = wvs.read()
            frame = cv2.resize(frame, (200,200))#(200,200)
            # ret , frame = cv2.imencode('.jpg',frame)
            # frame = frame.tobytes()
            jpg_as_text = zlib.compress(frame, 9)
            lenip = struct.pack('!I',len(IP))
            if quit1 == False:
                databytes = b"ACTIVE" + lenip + IP.encode() + jpg_as_text
            else:
                databytes = b"INTIVE" + lenip + IP.encode() + jpg_as_text
                print('Connection Terminated Mofo !!!')

            length = struct.pack('!I', len(databytes))
            bytesToBeSend = b''
            clientVideoSocket1.sendall(length)
            while len(databytes) > 0:
                if (1000 * CHUNK) <= len(databytes):
                    bytesToBeSend = databytes[:(1000 * CHUNK)]
                    databytes = databytes[(1000 * CHUNK):]
                    clientVideoSocket1.sendall(bytesToBeSend)
                else:
                    bytesToBeSend = databytes
                    clientVideoSocket1.sendall(bytesToBeSend)
                    databytes = b''
        if q == True:
            clientVideoSocket1.shutdown(1)
            clientVideoSocket1.close()
            wvs.stop()
            break  #######CHANGED########

def recvallVideo(clientVideoSocket, size):
    databytes = b''
    while len(databytes) != size:
        to_read = size - len(databytes)
        if to_read > (5000 * CHUNK):
            databytes += clientVideoSocket.recv(5000 * CHUNK)
        else:
            databytes += clientVideoSocket.recv(to_read)
    return databytes ########CHANGED########

def get_ip_address():
    s = S.socket(S.AF_INET, S.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip =  s.getsockname()[0]
    return ip

@app.route('/video')
def video():
    global startvideo
    if startvideo == 1:
        startvideo = 0
    else:
        startvideo = 1
    print ("Sucess Video")
    return "jskjdhsjk"

@app.route('/quit')
def quit112():
    global quit1
    quit1 = True
    print ("quit1 Sucess" , quit1)
    return render_template("home.html")

def ServerMedia():
    # HOST = input("Enter Host IP\n")
    HOST = '172.16.84.167'
    PORT_AUDIO = 10000
    PORT1 = 4000
    PORT2 = 5000
    PORT3 = 6000
    PORT4 = 7000
    PORT_UNIV = 8000
    lnF = 640*480*3
    CHUNK = 1024
    BufferSize = 4096
    quitUsers = {}
    addressesAudio = {}
    addresses = {}
    USERS = {'4000':[],'5000':[],'6000':[],'7000':[]}
    ports = {'10000':True,'8000':True,'4000':False,'5000':False,'6000':False,'7000':False}

    def accept(port, server1,server2,server3,server4):
        client1,addr1 = server1.accept()
        client2,addr2 = server2.accept()
        client3,addr3 = server3.accept()
        client4,addr4 = server4.accept()
        i = 0
        if port == '4000':
            PORTS = ['4000', '5000', '6000', '7000']
            print ("1st User detected")
        elif port == '5000':
            PORTS = ['5000', '4000', '6000', '7000']
            print ("2nd User detected")
        elif port == '6000':
            PORTS = ['6000', '4000', '5000', '7000']
            print ("3rd User detected")
        elif port == '7000':
            PORTS = ['7000', '4000', '5000', '6000']
            print ("4th User detected")
        clients = [client1, client2, client3, client4]
        for PORT in PORTS:
            if PORT != port:
                USERS[PORT].append(clients[i])
            i += 1
        return tuple(clients), PORTS

    def ConnectionsUniv():
        while True:
            client, addr = serverUniv.accept()
            addresses[client] = addr
            quitUsers[addr[0]] = False
            print("{} is connected!!".format(addr))
            for port in sorted(ports.keys()):
                if ports[port] == False:
                    client.sendall(port.encode())
                    ports[port] = True

                    if port == '4000':
                        clients, PORTS = accept(port, server1,server2,server3,server4)
                        Thread(target=ClientConnectionVideo, args=(port, client, clients, PORTS,)).start()
                    if port == '5000':
                        clients, PORTS = accept(port, server2,server1,server3,server4)
                        Thread(target=ClientConnectionVideo, args=(port, client, clients, PORTS,)).start()
                    if port == '6000':
                        clients, PORTS = accept(port, server3,server1,server2,server4)
                        Thread(target=ClientConnectionVideo, args=(port, client, clients, PORTS,)).start()
                    if port == '7000':
                        clients, PORTS = accept(port, server4,server1,server2,server3)
                        Thread(target=ClientConnectionVideo, args=(port, client, clients, PORTS,)).start()
                    break

    def ConnectionsSound():
        while True:
            clientAudio, addr = serverAudio.accept()
            print("{} is connected!!".format(addr))
            addressesAudio[clientAudio] = addr[0]
            Thread(target=ClientConnectionSound, args=(clientAudio, )).start()


    def ClientConnectionVideo(port, client, clients, PORTS):
        try:
            while True:
                if len(addresses)>1:
                    databytes = b''
                    client1 = clients[0]
                    lengthbuf = recvall(port, client1, 4)
                    databytes += lengthbuf
                    length, = struct.unpack('!I', lengthbuf)
                    STATUS  = recvall(port, client1, 6)
                    databytes += STATUS
                    STATUS = STATUS.decode()
                    databytes += recvall(port, client1, length-6)
                    broadcastVideo(port, databytes)
                    if STATUS == "INTIVE":
                        i = 0
                        quitUsers[addresses[client][0]] = True
                        del addresses[client]
                        ports[port] = False
                        for PORT in PORTS:
                            if PORT != port:
                                # clients[i].shutdown(1)
                                # clients[i].close()
                                USERS[PORT].remove(clients[i])
                            i += 1
                        # client1.shutdown(1)
                        # client1.close()
                        # client.shutdown(1)
                        # client.close()
                        break
        except:
            ports[port] = False

    def ClientConnectionSound(clientAudio):
        try:
            while True:
                if quitUsers[addressesAudio[clientAudio]] == False:
                    data = clientAudio.recv(BufferSize)
                    broadcastSound(clientAudio, data)
                else:
                    quitUsers[addressesAudio[clientAudio]] = False
                    del addressesAudio[clientAudio]
                    break
        except:
            pass


    def recvall(port, client1, BufferSize):
        databytes = b''
        i = 0
        while i != BufferSize:
            to_read = BufferSize - i
            if to_read > (1000 * CHUNK):
                databytes += client1.recv(1000 * CHUNK)
                i = len(databytes)
            else:
                databytes += client1.recv(to_read)
                i = len(databytes)
        return databytes

    def broadcastVideoFrame(client, data_to_be_sent, port):
        try:
            client.sendall(data_to_be_sent)
        except:
            # ports[port] = False
            # USERS[port] = []
            pass


    def broadcastVideo(port, data_to_be_sent):
        # threads = []
        for client in USERS[port]:
            frameThread = Thread(target=broadcastVideoFrame, args=(client, data_to_be_sent, port, ))
            frameThread.start()
            # threads.append(frameThread)
            frameThread.join()
        # for thread in threads:
            # thread.join()

    def broadcastSound(clientSocket, data_to_be_sent):
        temp = addressesAudio.copy()
        for clientAudio in temp:
            if clientAudio != clientSocket:
                try:
                    clientAudio.sendall(data_to_be_sent)
                except:
                    pass


    serverAudio = socket(family=AF_INET, type=SOCK_STREAM)
    server1 = socket(family=AF_INET, type=SOCK_STREAM)
    server2 = socket(family=AF_INET, type=SOCK_STREAM)
    server3 = socket(family=AF_INET, type=SOCK_STREAM)
    server4 = socket(family=AF_INET, type=SOCK_STREAM)
    serverUniv = socket(family=AF_INET, type=SOCK_STREAM)
    try:
        serverAudio.bind((HOST, PORT_AUDIO))
    except OSError:
        print("Server Audio is Busy")

    try:
        serverUniv.bind((HOST, PORT_UNIV))
    except OSError:
        print("Server Univ Busy")

    try:
        server1.bind((HOST, PORT1))
    except OSError:
        print("Server1 Busy")

    try:
        server2.bind((HOST, PORT2))
    except OSError:
        print("Server2 Busy")

    try:
        server3.bind((HOST, PORT3))
    except OSError:
        print("Server3 Busy")

    try:
        server4.bind((HOST, PORT4))
    except OSError:
        print("Server4 Busy")

    serverAudio.listen(4)
    AcceptThreadAudio = Thread(target=ConnectionsSound)
    AcceptThreadAudio.start()

    serverUniv.listen(4)
    server1.listen(4)
    server2.listen(4)
    server3.listen(4)
    server4.listen(4)
    print("Waiting for connection..")
    AcceptThreadUniv = Thread(target=ConnectionsUniv)
    AcceptThreadUniv.start()
    AcceptThreadUniv.join()
    serverUniv.close()

if __name__ == "__main__":
    app.run(debug=True)
