import cv2
from socket import socket, AF_INET, SOCK_STREAM
from imutils.video import FileVideoStream, FPS
from threading import Thread
from PIL import Image
import io
import numpy as np


HOST = "192.168.157.206"
PORT = 3000
BufferSize = 1024

def Recieve():
    while True:
        length = int(client.recv(8192).decode("utf-8"))
        while True:
            receivingBuffer = client.recv(BufferSize)
            if not receivingBuffer:
                break
            data = b''
            if len(data) <= length:
                to_read = length - len(data)
                data += client.recv(4096 if to_read > 4096 else to_read)

        pilBytes = io.BytesIO(data)
        pilImage = Image.open(pilBytes)
        cvImage = cv2.cvtColor(np.array(pilImage), cv2.COLOR_RGB2BGR)
        cv2.imshow("Video", cvImage)


def Send():
    fvs = FileVideoStream(0).start()
    while fvs.more():
        frame = fvs.read()

        cvImage = cv2.cvtColor(np.array(pilImage), cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(cvImage)
        b = io.BytesIO()
        pil.save(b, 'jpeg')
        imgBytes = b.getvalue()

        length = str(len(imgBytes))
        client.sendall(length.encode(encoding='utf_8'))
        client.sendall(imgBytes)


client = socket(family=AF_INET, type=SOCK_STREAM)
client.connect((HOST, PORT))

RecieveThread = Thread(target=Recieve).start()
SendThread = Thread(target=Send).start()
