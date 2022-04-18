'''
This module defines the behaviour of a client in your Chat Application
'''
import sys
import getopt
import socket
import random
from threading import Thread
import os
import threading
import util


'''
Write your code inside this class. 
In the start() function, you will read user-input and act accordingly.
receive_handler() function is running another thread and you have to listen 
for incoming messages in this function.
'''


class Client:
    '''
    This is the main Client Class. 
    '''

    def __init__(self, username, dest, port):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(None)
        self.name = username
        self.status=False

    def start(self):
        '''
        Main Loop is here
        Start by sending the server a JOIN message.
        Waits for userinput and then process it
        '''
        self.sock.connect((self.server_addr,self.server_port))
        self.status=True
        m=util.make_message("join",1,self.name)
        self.sock.send(m.encode("utf-8"))
        # tc=threading.Thread(target=Client.ask_input,args=())
        # tc.daemon=True
        while(self.status==True):
            u=input("")

            #if the user input if not a valid command
            # print("incorrect user input format")
            
            #if the input is list
            if u=="list":
                Client.handle_list(self,u)

            #if the input is quit

            elif u=="quit":

                Client.handle_quit(self)

            
            #if the client wants to send file
            elif "file" in u:
                li=u.split(" ")
                #strip thee "file" part from the message
                m=li[1:]
                m=" ".join(m)
                Client.handle_file(self,m)


                


            elif "msg" in u:
                #if user wants to send a message

                #take out the number of recipients of the message
                li=u.split(" ")
                num_recipients=int(li[1])
                #strip the "msg" part and put the rest of it in the message
                m=li[1:]
                m=" ".join(m)
                Client.handle_msg(self,m)

            elif u=="help":
                print(""" 
                
 _____ _           _    ___               
/  __ \ |         | |  / _ \              
| /  \/ |__   __ _| |_/ /_\ \_ __  _ __   
| |   | '_ \ / _` | __|  _  | '_ \| '_ \  
| \__/\ | | | (_| | |_| | | | |_) | |_) | 
 \____/_| |_|\__,_|\__\_| |_/ .__/| .__/  
                            | |   | |     
                            |_|   |_|     

                """)

                print("")
                print("Possible user inputs and their formats are as follows: ")
                print("")
                print("To view the usernames of clients connected to application-server: ","list")
                print("")
                print("To send message to client(s): ","msg <number_of_users> <username1> <username2> … <message>")
                print("")
                print("To send a file to client(s): ",": file <number_of_users> <username1> <username2> … <file_name>")
                print("")
                print("To view all possible user inputs and their formats: ","help")
                print("")
                print("To quit from the application-server: ","quit")
                print("")


            

            else:

                print("incorrect userinput format")




            

        # while(1):
        #     #implement threading here
        # #  (  tc.start()
        #     pass
        self.sock.close()

       
    def handle_file(self,m):
        li=m.split(" ")
        num_clients=int(li[0])
        file_name=li[1+num_clients]

        list_recipients=li[1:1+num_clients]
        list_recipients=" ".join(list_recipients)
        file1 = open(file_name,"r+") 
        file_content=file1.readlines()
        content_string=" ".join(file_content)
        message=f"{num_clients} {list_recipients} {file_name} {content_string}"
        msg=util.make_message("send_file",4,message)
        Client.send_msg(self,msg)








    def handle_msg(self,m):

        msg=util.make_message("send_message",4,m)
        Client.send_msg(self,msg)
    


    def handle_quit(self):
        #send disconnect message to server
        m=util.make_message("disconnect",1,self.name)
        Client.send_msg(self,m)
        self.status=False

        self.sock.close()
        print("quitting")
        sys.exit()

    
    
    #handles the case where the input is list 
    def handle_list(self,i):
        #send request users  list message to server
        m=util.make_message("request_users_list",2)
        Client.send_msg(self,m)

    
    
    def send_msg(self,m):
        self.sock.send(m.encode("utf-8"))
    
    
    def receive_handler(self):
        '''
        Waits for a message from server and process it accordingly
        '''
        while True:
            
                if self.status:
                    m=self.sock.recv(4096)
                    m=m.decode("utf-8")
                    

                    #if the server sends err_server_full message
                    if m=="err_server_full":
                        self.status=False

                        print("disconnected: server full")
                        sys.exit()
                        break


                    #if server sends err_username_unavailable message
                    if m=="err_username_unavailable":
                        self.status=False

                        print("disconnected: username not available")
                        sys.exit()
                        break


                    #if the client recieves err_unknown_message message

                    if m=="err_unknown_message":
                        self.status=False
                        print("disconnected: server received an unknown command")

                        sys.exit()


                        
                        break
                    
                    #if the server sends the list  of usernames
                    if "response_users_list" in m:
                        try:
                            li=m.split()
                            list_users=li[2:]
                            users_string=" ".join(list_users)
                            print(f"list: {users_string}")
                        except Exception as e:
                            print(e)

                            #if server forwards message
                    if "forward_message" in m:
                        li=m.split(" ")
                        sender=li[1]
                        message=li[2:]
                        message=" ".join(message)
                        #print the recieved message
                        print(f"msg: {sender}: {message}")
                    
                    if "forward_file" in m:
                        #if the server forwards a file
                        li=m.split(" ")
                        sender=li[1]
                        sender="".join(sender)

                        file_name=li[2]
                        file_name="".join(file_name)

                        update_file_name= f"{self.name}_{file_name}"
                        file_contents=li[3:]
                        file_contents=" ".join(file_contents)
                        print(f"file: {sender}: {file_name}")
                        new_file=open(update_file_name,"w")
                        new_file.write(file_contents)
                        new_file.close()

                            


        



        

# Do not change this part of code
if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our Client module completion
        '''
        print("Client")
        print("-u username | --user=username The username of Client")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-h | --help Print this help")
    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "u:p:a", ["user=", "port=", "address="])
    except getopt.error:
        helper()
        exit(1)

    PORT = 15000
    DEST = "localhost"
    USER_NAME = None
    for o, a in OPTS:
        if o in ("-u", "--user="):
            USER_NAME = a
        elif o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a

    if USER_NAME is None:
        print("Missing Username.")
        helper()
        exit(1)

    S = Client(USER_NAME, DEST, PORT)
    try:
        # Start receiving Messages
        T = Thread(target=S.receive_handler)
        T.daemon = True
        T.start()
        # Start Client
        S.start()
    except (KeyboardInterrupt, SystemExit):
        sys.exit()
