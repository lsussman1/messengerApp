import socket
from socket import *
import threading
import time
import datetime as dt
import sys

#global variables:
port = int(sys.argv[1])
blockDuration = int(sys.argv[2])
timeOut=int(sys.argv[3])
buffer = 4096
clients = {}
times = {}
blocked = {}
blockLogin = []
login = {}
offline = {}

def listen(s):
    s.listen(1)
    while True:
        connection, address = s.accept()
        threading.Thread(target = listenToClient,args = (connection,address)).start()

def listenToClient(connection, address):
    global offline
    global login
    username = userAuthentication(connection)
    #block after 3 fails:
    split = username.split(' ', 1)
    if split[0] == "blockLogin":
        print("blocking from login: " + split[1])
        sendStatement(connection, "3 unsuccessful login attempts. Wait "+ str(blockDuration) + " seconds and try again")
        blockLogin.append(split[1])
        timer = threading.Timer(blockDuration, listenToClient, args = (connection,address))
    #let others know user has logged in, store pertinent user info in dictionaries
    broadcast(username + " has logged in", username)
    login[username]= True
    clients[username] = connection
    times[username] = time.time()
    blocked[username] = []
    if username not in offline:
        offline[username] = []

    #if havent received data for timeout seconds, log out client #NEED TO IMPLEMENT
    while login[username]:
        for item in offline[username]:
            responseHandler(item, username)
            offline[username].remove(item)
        data = connection.recv(buffer)
        if data:
            responseHandler(data, username)

def Main():
    s = socket(AF_INET, SOCK_STREAM)
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    host = ''
    s.bind((host, port))
    listen(s)

def sendQuestion(connection, question):
    message = "question " + question
    try:
        connection.send(message.encode('utf-8'))
    except:
        print("connection messed up")

def sendStatement(connection, statement):
    message = "statement " + statement
    try:
        connection.send(message.encode('utf-8'))
    except:
        print("connection messed up")

def responseHandler(data, username):
    global login
    global blocked
    global offline
    global times
    global clients
    valid = False
    decoded = data.decode('utf-8')
    if "\n" in decoded:
        decoded = decoded.strip('\n')
    split = decoded.split(' ', 1)
    head = split[0]
    if split[0]!=decoded:
        message = split[1]
        if head == "message":
            valid = True
            split2 = message.split(' ', 2)
            via = split2[0]
            to = split2[1]
            if (to in clients) and (login[to]):
                if via not in blocked[to]:
                    msgcontent = username + ": " + split2[2]
                    sendStatement(clients[to], msgcontent)
                else: 
                    sendStatement(clients[via], "Your message could not be delivered as the recipient has blocked you.")
            elif (to in login) and (not login[to]):
                print("offline: "+ to)
                offline[to].append(data)
            else: 
                sendStatement(clients[via], "Recipient is not a user")
        elif head == "broadcast":
            valid = True
            broadcast(message, username)
        elif head == "whoelsesince":
            valid = True
            whoelsesince(username, int(message))
        elif head == "block":
            valid = True
            if message == username:
                sendStatement(clients[username], "Error. Cannot block self.")
            else:
                sendStatement(clients[username], message + " is blocked")
                blocked[username].append(message)
        elif head == "unblock":
            valid = True
            if message not in blocked[username]:
                sendStatement(clients[username], "Error. " + message + " was not blocked")
            else:
                sendStatement(clients[username], message + " is unblocked")
                blocked[username].remove(message)
    elif decoded == "whoelse":
        valid = True
        whoelse(username)
    elif decoded == "logout":
        valid = True
        sendStatement(clients[username], "You have logged out.")
        del clients[username]
        del times[username]
        login[username] = False
        broadcast(username + " has logged out")
    elif decoded == "":
        valid = True
        None
    if valid == False:
        sendStatement(clients[username], "Error. Invalid command.")

def userAuthentication(connection):
    credentials = dictionaryCredentials()
    fails = 0

    sendQuestion(connection, "Enter your username:")
    data = connection.recv(buffer)
    if data:
        username = data.decode('utf-8')
        if "\n" in username:
            username = decoded.strip('\n')
    else:
        print("recived message not valid")

    while fails < 3:
        print("fails: "+str(fails))

        sendQuestion(connection, "Enter your password:")
        data = connection.recv(buffer)
        if data:
            password = data.decode('utf-8')
            if "\n" in password:
                password = decoded.strip('\n')
            password = data.decode('utf-8')
        else:
            print("recived message not valid")

        if username in credentials and credentials[username] == password:
            #sendStatement(connection, "Logged in! :)")
            print("returning: " + username)
            message = "username " + username
            connection.send(message.encode('utf-8'))
            return username
        else:
            sendStatement(connection, "Invalid login. Try again.\n")     
            fails += 1
    print("blockLogin")
    return "blockLogin " + username

def whoelse(username):
    for item in clients:
        if item != username:
            sendStatement(clients[username], item)

def whoelsesince(username, since):
    timeSince = time.time() - since
    for item in times:
        if (times[item] >= timeSince) & (item != username):
            sendStatement(clients[username], item)

def broadcast(broadcast, via):
    global blocked
    for item in clients:
        if via in blocked[item]:
            sendStatement(clients[via], "Your message could not be delivered to some recipients.")
        elif item != via:
            sendStatement(clients[item], via + ": " + broadcast)

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