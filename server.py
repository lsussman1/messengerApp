import socket
from socket import *
import threading
#from thread import *
import time
import datetime as dt
import sys

#global variables:
port = int(sys.argv[1])
blockTime = int(sys.argv[2])
timeout=int(sys.argv[3])
clients = []
#lock = threading.Lock()

#inspiration from https://stackoverflow.com/questions/23828264/how-to-make-a-simple-multithreaded-socket-server-in-python-that-remembers-client
class clientThread(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)
        #set sock opt
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.bind((self.host, self.port))
    # main thread that listens for other connections
    def listen(self):
        self.socket.listen(1)
        while True:
            connection, address = self.socket.accept()
            threading.Thread(target = self.listenToClient,args = (connection,address)).start()
    #client threads that listen for messages
    def listenToClient(self, connection, address):
        buffer = 1024
        login = False
        while True:
            print(address + " connected\n")
            connection.send("enter username:".encode('utf-8'))
            try:
                data = connection,recv(buffer)
                if data:
                    print(address + " connected\n")
                    clients.append(address)
                    connection.send("enter username:")
                else:
                    print("client disconnected")
            except:
                connection.close()
                return False

# thread fuction 
def threaded(connection): 
    while True: 
        # data received from client 
        data = connection.recv(1024) 
        if not data: 
            print('Bye') 
            # lock released on exit 
            lock.release() 
            break
        # reverse the given string from client 
        data = data[::-1] 
        # send back reversed string to client 
        connection.send(data) 
    c.close() 

def Main():
    

    #will store clients info in this list (threads)
    #clients=[]
    # would communicate with clients after every second
    UPDATE_INTERVAL= 1
    clientThread('', port).listen()
    #s = socket(AF_INET, SOCK_STREAM)
    #host = ''
    #s.bind((host, port))   
    while False: 
        s.listen(1)
        connection, address = s.accept()  
        lock.acquire() 
        print('Connected to :', address[0], ':', address[1]) 
  
        # Start a new thread and return its identifier 
        start_new_thread(threaded, (connection,)) 
    #s.close() 

def mssgsend(client, message):
    print("hi")

def userAuthentication():
    credentials = credentials()
    fails = 0
    while True:
        username = input("Enter your username:")
        if username in credentials:
            password = input("Enter your password:")
            if credentials[username] == password:
                return True
        else:
            print("Invalid username")
        fails += 1
        #for blocking after 3, implement later


# Returns dictionary with username-password pairs
def credentials():
    d = {}
    credentials = open("credentials.txt", "rw+")
    for line in credentials:
        (username, password) = line.split()
        d[username] = password
    return d

if __name__ == '__main__': 
    Main() 