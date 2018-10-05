from socket import socket, AF_INET, SOCK_STREAM
from threading import Thread
import pyaudio
from array import array


HOST = input("Enter Server IP\n")
PORT = 4000
BufferSize = 4096

FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100
CHUNK=1024

def SendAudio():
    while True:
        data = stream.read(CHUNK)
        dataChunk = array('h', data)
        vol = max(dataChunk)
        if(vol > 500):
            print("Recording Sound...")
        else:
            print("Silence..")
        client.sendall(data)


def RecieveAudio():
    while True:
        data = recvall(BufferSize)
        stream.write(data)

def recvall(size):
    databytes = b''
    while len(databytes) != size:
        to_read = size - len(databytes)
        if to_read > (4 * CHUNK):
            databytes += client.recv(4 * CHUNK)
        else:
            databytes += client.recv(to_read)
    return databytes

client = socket(family=AF_INET, type=SOCK_STREAM)
client.connect((HOST, PORT))

audio=pyaudio.PyAudio()
stream=audio.open(format=FORMAT,channels=CHANNELS, rate=RATE, input=True, output = True,frames_per_buffer=CHUNK)


RecieveAudioThread = Thread(target=RecieveAudio).start()
SendAudioThread = Thread(target=SendAudio).start()
