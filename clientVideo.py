import cv2
from socket import socket, AF_INET, SOCK_STREAM
from imutils.video import FileVideoStream, FPS
from threading import Thread
# from PIL import Image
import base64
# import io
import numpy as np


HOST = "192.168.157.206"
PORT = 3000
BufferSize = 4096

def Recieve():
    print("Client is recieving...")
    while True:
        length = int(client.recv(2 * BufferSize).decode("utf-8"))
        data = b''
        while True:
            if len(data) < length:
                to_read = length - len(data)
                data += client.recv(BufferSize if to_read > BufferSize else to_read)
            else:
                break

        # pilBytes = io.BytesIO(data)
        # pilBytes.seek(0)
        # pilImage = Image.open(pilBytes)
        # cvImage = cv2.cvtColor(np.array(pilImage), cv2.COLOR_RGB2BGR)
        # cv2.imshow("Video", np.array(pilImage))

        img = base64.b64decode(data)
        npimg = np.fromstring(img, dtype=np.uint8)
        source = cv2.imdecode(npimg, 1)
        cv2.imshow("Stream", source)
        cv2.waitKey(1)


def Send():
    fvs = FileVideoStream(0).start()
    while fvs.more():
        frame = fvs.read()

        # cvImage = cv2.cvtColor(np.array(frame), cv2.COLOR_BGR2RGB)
        # pil = Image.fromarray(cvImage)
        # b = io.BytesIO()
        # pil.save(b, 'jpeg')
        # imgBytes = b.getvalue()

        encoded, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer)

        length = str(len(jpg_as_text))
        print("client is sending...")
        client.sendall(length.encode(encoding='utf_8'))
        client.sendall(jpg_as_text)


client = socket(family=AF_INET, type=SOCK_STREAM)
client.connect((HOST, PORT))

RecieveThread = Thread(target=Recieve).start()
SendThread = Thread(target=Send).start()
