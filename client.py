import socket
import threading
import select
import sys
import time

#Server would be running on the same host as Client
host = sys.argv[1]
port = int(sys.argv[2])
buffer = 4096
UPDATE_INTERVAL = 0.5
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def Main(): 
    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, port)) 
        print("connected to "+host)
    except:
        print("---> Server not running")
    recv_thread=threading.Thread(name="reciever", target=reciever)
    recv_thread.daemon=True

    send_thread=threading.Thread(name="sender",target=sender)
    send_thread.daemon=True

    #send and recieve simultaniuosly
    while True:
        recv_thread.start()
        send_thread.start()
        time.sleep(UPDATE_INTERVAL)
        recv_thread.join()
        send_thred.join()

def reciever():
    while True:
        print("here rec")
        data = s.recv(buffer)
        print(data)
        while data:
            print("rec data")
            recieveHandler(data, s)
        time.sleep(UPDATE_INTERVAL)
        print("time sleep")

def sender():
    message = ""
    while True:
        sys.stdout.write('> ')
        print("here")
        message = sys.stdin.readline()
        if message != "": 
            print("here mess")          
            sendHandler(message, s)
        time.sleep(UPDATE_INTERVAL)
        print("time sleep")
    recieve.close()
    send.close()

#doesn't succesfully remove header for everything
def recieveHandler(encoded, s):
    decoded = encoded.decode('utf-8')
    split = decoded.split(' ', 1)
    head = split[0]
    message = split[1]

    if head == "question":
        response = input(message + " ")
        encoded = response.encode('utf-8')
        s.sendto(encoded, (host, port))
    elif head == "statement":
        print(message)
    else:
        print("not expected header")

def sendHandler(decoded, s):
    encoded = decoded.encode('utf-8')
    s.sendto(encoded, (host, port))
    
    
if __name__ == '__main__': 
    Main() 