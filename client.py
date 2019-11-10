from socket import *
import sys

#Server would be running on the same host as Client
IP = sys.argv[1]
port = int(sys.argv[2])

def Main(): 
    s = socket(AF_INET, SOCK_STREAM)
    # connect to server on local computer 
    s.connect((IP,port)) 
    # message you send to server 
    while True: 

        # message sent to server 
        # messaga received from server 
        data = s.recv(1024) 

        # print the received message 
        # here it would be a reverse of sent message 
        print('Received from the server :',str(data.decode('ascii'))) 
  
        # ask the client whether he wants to continue 
        ans = input('\nDo you want to continue(y/n) :') 
        if ans == 'y': 
            continue
        else: 
            break
    # close the connection 
    s.close() 

if __name__ == '__main__': 
    Main() 