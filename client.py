import socket
import threading
import select
import sys
import os
import time

#Server would be running on the same host as Client
host = sys.argv[1]
port = int(sys.argv[2])
buffer = 4096
UPDATE_INTERVAL = 0.001
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
login = False
myUsername = ''

def Main(): 
    #s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    global login
    try:
        s.connect((host, port)) 
        print("connected to "+host)
    except:
        print("---> Server not running")

    #while authenticiating, only listen for incoming data
    while login == False:
        data = s.recv(buffer)
        if data:
            recieveHandler(data, s)
    
    #after login = True, begin a recieveing and sending thread
    recv_thread=threading.Thread(name="reciever", target=reciever)
    recv_thread.daemon=True

    send_thread=threading.Thread(name="sender",target=sender)
    send_thread.daemon=True

    #send and recieve simultaniuosly
    while login:
        send_thread.start()
        recv_thread.start()
        recv_thread.join()
        send_thread.join()

def reciever():
    while True:
        data = s.recv(buffer)
        if data:
            recieveHandler(data, s)
            #time.sleep(UPDATE_INTERVAL)

def sender():
    global login
    global myUsername
    while login:
        sys.stdout.write('> ')
        sys.stdout.flush()
        message = sys.stdin.readline()
        if message: 
            split = message.split(' ', 1)
            #if sending message, must tag on your username incase the reciever has blocked you
            if split[0] == "message":
                message = split[0] + " " + myUsername + " " + split[1]
            sendHandler(message, s)
            #time.sleep(UPDATE_INTERVAL)

#doesn't succesfully remove header for everything
def recieveHandler(encoded, s):
    global login
    global myUsername
    sys.stdout.flush()
    decoded = encoded.decode('utf-8')
    split = decoded.split(' ', 1)
    head = split[0]
    message = split[1]
    if head == "question":
        response = input("> " +message + " ")
        encoded = response.encode('utf-8')
        s.sendto(encoded, (host, port))
    elif head == "username":
        myUsername = message
        login = True
        print("> Logged in! :)")
    elif head == "statement":
        print("> " + message)
        if message == "You have logged out.":
            login = False
            os._exit(0)
    else:
        print("not expected header")

def sendHandler(decoded, s):
    encoded = decoded.encode('utf-8')
    s.sendto(encoded, (host, port))
    
if __name__ == '__main__': 
    Main() 