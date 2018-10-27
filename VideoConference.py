import cv2
import socket as S
from socket import socket, AF_INET, SOCK_STREAM
from webcamVideoStream import WebcamVideoStream
import pyaudio
from array import array
from threading import Thread
import numpy as np
import zlib
import struct

# HOST = input("Enter Server IP\n")
HOST = '172.16.84.73'
PORT_AUDIO = 10000
PORT1 = 4000
PORT2 = 5000
PORT3 = 6000
PORT4 = 7000
PORT_UNIV = 8000

BufferSize = 4096
CHUNK=1024
###
lnF = 200*200*3
###
FORMAT=pyaudio.paInt16
CHANNELS=2
RATE=44100

ports = {'10000':True,'8000':True,'4000':False,'5000':False,'6000':False,'7000':False}
USERS = {}
imageStream = np.array([])
quit1=False

def SendAudio():
    global quit1
    while True:
        if quit1 == False:
            data = stream.read(CHUNK)
            dataChunk = array('h', data)
            vol = max(dataChunk)
            if(vol > 500):
                #print("Recording Sound...")
                clientAudioSocket.sendall(data)
            else:
                #print("Silence..")
                pass
        else:
            break

def RecieveAudio():
    global quit1
    while True:
        if quit1 == False:
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
    IP = get_ip_address()
    global quit1
    while True:

            frame = wvs.read()
            cv2_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (200, 200))
            frame = np.array(frame, dtype = np.uint8).reshape(1, lnF)
            jpg_as_text = bytearray(frame)
            jpg_as_text = zlib.compress(jpg_as_text, 9)

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
                if (5000 * CHUNK) <= len(databytes):
                    bytesToBeSend = databytes[:(5000 * CHUNK)]
                    databytes = databytes[(5000 * CHUNK):]
                    clientVideoSocket1.sendall(bytesToBeSend)
                else:
                    bytesToBeSend = databytes
                    clientVideoSocket1.sendall(bytesToBeSend)
                    databytes = b''
            if quit1 == True:
                break



def RecieveFrame(clientVideoSocket):
    IP = get_ip_address()
    global quit1
    global imageStream
    while quit1==False:

        lengthbuf = recvallVideo(clientVideoSocket, 4)
        print('Lengthbuf - ',lengthbuf)
        length, = struct.unpack('!I', lengthbuf)
        print('Length - ',length)
        print (length)
        databytes = recvallVideo(clientVideoSocket, length)
        print('Status - ',databytes[:6])
        databytes1 = databytes
        STATUS = databytes[:6].decode()
        if STATUS == "ACTIVE" or STATUS == "INTIVE":
            lenip, = struct.unpack('!I',databytes[6:10])
            ipUser = databytes[10:10+int(lenip)]
            databytes = databytes[(len(STATUS)+4+len(ipUser)):]
            img = zlib.decompress(databytes)
            # img = img[len(IP)+6:]

            if len(databytes1) == length:
#                 print("Recieving Media..")
#                 print("Image Frame Size:- {}".format(len(img)))
                img = np.array(list(img))
                img = np.array(img, dtype = np.uint8).reshape(200, 200, 3)
                img = cv2.resize(img,(640,480))
                if ipUser not in USERS:
                    USERS[ipUser] = img
                else:
                    if STATUS == "ACTIVE":
                        USERS[ipUser] = img
                    elif STATUS == "INTIVE":
                        del USERS[ipUser]



            else:
                print("Data CORRUPTED")
        else:
            print('Status Error!:-    ',STATUS)
            continue


def display():
    global quit1
    global USERS
    while True:
        US = USERS.copy()
        if len(US) == 1:

            for user in US:
                background = cv2.resize(US[user], (640, 480))
                overlay = wvs.read()
                overlay = cv2.resize(overlay, (200, 150))
                s_img = overlay
                finalImage = cv2.resize(background,(1280,720))
                x_offset=1080
                y_offset=570
                finalImage[y_offset:y_offset+s_img.shape[0], x_offset:x_offset+s_img.shape[1]] = s_img

        elif len(US) == 2:
            frames = []
            for ip in US:
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

        elif len(US) == 3:
            frames = []
            for ip in US:
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
            finalImage = cv2.resize(finalImage, (1080, 720))

        elif len(US) == 0:
            finalImage = wvs.read()
            finalImage = cv2.resize(finalImage, (1080, 720))


        cv2.imshow("Stream", finalImage)
        if cv2.waitKey(1) == 27:
            quit1 = True
            cv2.destroyAllWindows()
            wvs.stop()
            break



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
clientVideoSocket1.connect((HOST, int(PORTNUMBER)))
ports[PORTNUMBER] = True
SendFrameThread = Thread(target=SendFrame).start()

for portnos in sorted(ports.keys()):
    if ports[portnos] == False:
        clientVideoSocket2 = socket(family=AF_INET, type=SOCK_STREAM)
        clientVideoSocket2.connect((HOST, int(portnos)))
        ports[portnos] = True
        RecieveFrameThread1 = Thread(target=RecieveFrame, args=(clientVideoSocket2, )).start()
        print(portnos,' - Connected !')
        break

for portnos in sorted(ports.keys()):
    if ports[portnos] == False:
        clientVideoSocket3 = socket(family=AF_INET, type=SOCK_STREAM)
        clientVideoSocket3.connect((HOST, int(portnos)))
        ports[portnos] = True
        RecieveFrameThread2 = Thread(target=RecieveFrame, args=(clientVideoSocket3, )).start()
        print(portnos,' - Connected !')
        break

for portnos in sorted(ports.keys()):
    if ports[portnos] == False:
        clientVideoSocket4 = socket(family=AF_INET, type=SOCK_STREAM)
        clientVideoSocket4.connect((HOST, int(portnos)))
        ports[portnos] = True
        RecieveFrameThread3 = Thread(target=RecieveFrame, args=(clientVideoSocket4, )).start()
        print(portnos,' - Connected !')
        break


audio=pyaudio.PyAudio()
stream=audio.open(format=FORMAT,channels=CHANNELS, rate=RATE, input=True, output = True,frames_per_buffer=CHUNK)

IP = get_ip_address()


SendAudioThread = Thread(target=SendAudio)
RecieveAudioThread = Thread(target=RecieveAudio)
DisplayThread = Thread(target=display)
RecieveAudioThread.start()
DisplayThread.start()
# SendAudioThread.start()
# SendAudioThread.join()