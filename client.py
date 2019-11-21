import socket
import threading
import select
import sys
import os
import time

host = sys.argv[1]
port = int(sys.argv[2])
buffer = 4096
UPDATE_INTERVAL = 0.001
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
login = False
myUsername = ''

def Main(): 
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

#recieving thread: continuosly loops, checking for recived data. If data, handle.
def reciever():
    while True:
        data = s.recv(buffer)
        if data:
            recieveHandler(data, s)

#sending thread: continously checks if the user has typed a command. If  they do, handle.
def sender():
    global login
    global myUsername
    while login:
        sys.stdout.write('> ')
        sys.stdout.flush()
        message = sys.stdin.readline()
        if message: 
            sendHandler(message, s)

#handles types of data the server may send
#the server sends data in the format [header] + [data]
def recieveHandler(encoded, s):
    global login
    global myUsername
    sys.stdout.flush()
    decoded = encoded.decode('utf-8')
    split = decoded.split(' ', 1)
    head = split[0]
    message = split[1]
    #if they recieve a question, imediaetly get user input and send answer back to server
    if head == "question":
        response = input("> " +message + " ")
        encoded = response.encode('utf-8')
        s.sendto(encoded, (host, port))
    #if they recieve username, store username and confirm login to user
    elif head == "username":
        myUsername = message
        login = True
        print("> Logged in! :)")
    #if they recieve a statement, simply print it to the screen.
    #for certain messages, close the client application
    elif head == "statement":
        print("> " + message)
        if message == "You have logged out.":
            login = False
            os._exit(0)
        if message.split('.', 1)[0] == "3 unsuccessful login attempts":
            os._exit(0)
    else:
        print("not expected header")

#encodes user messsage and ships it off to server
def sendHandler(decoded, s):
    encoded = decoded.encode('utf-8')
    s.sendto(encoded, (host, port))
    
if __name__ == '__main__': 
    Main() 