from socket import *
import select
import sys

#Server would be running on the same host as Client
IP = sys.argv[1]
port = int(sys.argv[2])
buffer = 4096
UPDATE_INTERVAL = 0.5

def Main(): 
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((IP, port)) 
    s.settimeout(UPDATE_INTERVAL)
    message = ""
    while message != 'logout': 
        sys.stdout.write('>')
        if message != "":           
            sendHandler(message, s)
        try:
            data = s.recv(buffer)
            while data:
                recieveHandler(data, s)
                data = None
        except timeout:
            sys.stdout.write('>')
            message = sys.stdin.readline()

    s.close() 

#doesn't succesfully remove header for everything
def recieveHandler(encoded, s):
    decoded = encoded.decode('utf-8')
    print(decoded)
    split = decoded.split(' ', 1)
    head = split[0]
    message = split[1]
    if head == "question":
        response = input(message + " ")
        encoded = response.encode('utf-8')
        s.sendto(encoded, (IP, port))
    elif head == "statement":
        print(message)
    else:
        print("not expected header")

def sendHandler(decoded, s):
    encoded = decoded.encode('utf-8')
    s.sendto(encoded, (IP, port))
    
    
if __name__ == '__main__': 
    Main() 