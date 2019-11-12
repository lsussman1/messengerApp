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
timeOut=int(sys.argv[3])
clients = {}
times = {}
buffer = 4096
#lock = threading.Lock()

#inspiration from https://stackoverflow.com/questions/23828264/how-to-make-a-simple-multithreaded-socket-server-in-python-that-remembers-client
class clientThread(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, SOCK_STREAM)
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
        #at connection of new client, authenticate and store deatils in dictionary
        username = userAuthentication(connection)
        broadcast(username + " has logged in")
        clients[username] = connection
        times[username] = time.time()
        #always listen for data coming in from client, if recieve data, handle request
        #if havent received data for timeout seconds, 
        while True:
            data = connection.recv(buffer)
            if data:
                responseHandler(data, username)
            #except:
           #     print('except')
            #    broadcast(username + " has logged out")
             #   del clients[username]
              #  connection.close()
               # return

def Main():
    #run listening thread on localhost:
    clientThread('', port).listen()

#REMEMBER TO PUT A SPACE AFTER HEADRER WORD YA DUMB IDIOT
def sendQuestion(connection, question):
    message = "question " + question
    connection.send(message.encode('utf-8'))
    while True:
        data = connection.recv(buffer).decode('utf-8')
        if data:
            return data

def sendStatement(connection, statement):
    message = "statement " + statement
    connection.send(message.encode('utf-8'))

def responseHandler(data, username):
    decoded = data.decode('utf-8')
    print(decoded)
    if "\n" in decoded:
        decoded = decoded.strip('\n')
    print(decoded)
    split = decoded.split(' ', 1)
    head = split[0]
    if split[0]!=decoded:
        message = split[1]
        if head == "message":
            split2 = message.split(' ', 1)
            user = split2[0]
            msgcontent = username + ": " + split2[1]
            connection = clients[user]
            sendStatement(connection, msgcontent)
            print("sent: " + message)
        if head == "broadcast":
            broadcast(message)
        if head == "whoelsesince":
            whoelsesince(username, int(message))
        if head == "block":
            print("block")
        if head == "unblock":
            print("unblock")
    elif decoded == "whoelse":
        whoelse(username)
    elif decoded == "logout":
        print("logout")

def userAuthentication(connection):
    credentials = dictionaryCredentials()
    fails = 0
    while True:
        if fails == 3:
            break
        username = sendQuestion(connection, "Enter your username:")
        print(username)
        password = sendQuestion(connection, "Enter your password:")
        print(password)
        if username in credentials and credentials[username] == password:
            sendStatement(connection, "Logged in! :)")
            print("returning: " + username)
            return username
        else:
            sendStatement(connection, "Invalid login. Try again.\n")     
            fails += 1

def whoelse(username):
    for item in clients:
        if item != username:
            sendStatement(clients[username], item)

def whoelsesince(username, time):
    timeSince = time.time() - time
    for item in times:
        if times[item] >= timeSince & item != username:
            sendStatement(clients[username], item)

def broadcast(broadcast):
    for item in clients:
        sendStatement(clients[item], broadcast)

def listCurrentUsers(connection):
    for item in clients:
        sendStatement(connection, item)

# Returns dictionary with username-password pairs
def dictionaryCredentials():
    d = {}
    credentials = open("credentials.txt", "r+")
    for line in credentials:
        (username, password) = line.split()
        d[username] = password
    return d

if __name__ == '__main__': 
    Main() 