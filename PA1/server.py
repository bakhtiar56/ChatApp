'''
This module defines the behaviour of server in your Chat Application
'''
import sys
import getopt
import socket
import util
import threading


class Server:

    '''
    This is the main Server Class. You will to write Server code inside this class.
    '''

    def __init__(self, dest, port):
        self.server_addr = dest
        self.server_port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(None)
        self.sock.bind((self.server_addr, self.server_port))
        self.client_info = dict()

    def start(self):
        '''
        Main loop.
        continue receiving messages from Clients and processing it
        '''
        self.sock.listen(util.MAX_NUM_CLIENTS)
        while True:
            cl_soc, cl_addr = self.sock.accept()
            addrr = (cl_soc, cl_addr)
            t1 = Server.make_thread(self, addrr)
            t1.start()

    def get_username(self, sock):
        for x, y in self.client_info.items():
            if y[0] == sock:
                return x

    def close_soc(self, sock):
        sock.close()

    def send_message(self, sock, m):
        sock.send(m.encode("utf-8"))

    def get_message(self, sock):

        m = sock.recv(4096)
        return m.decode("utf-8")

    def make_thread(self, ar):

        t = threading.Thread(target=Server.receive_handler, args=(self, ar))
        t.daemon = True
        return t

    def receive_handler(self, ar):
        client_running = True
        while(client_running):

            (cl_soc, cl_addr) = ar
            m = Server.get_message(self, cl_soc)

            # join message
            if "join" in m:
                try:
                    li = m.split(" ")
                    user_name = li[1]

                    # first check, if server is full
                    if len(self.client_info) == util.MAX_NUM_CLIENTS:
                        print("disconnected: server full")
                        m = util.make_message("err_server_full", 2)
                        Server.send_message(self, cl_soc, m)
                        cl_soc.close()
                        break
                    # then check if the username is already taken by another client
                    if user_name in self.client_info.keys():
                        print("disconnected: username not available")
                        m = util.make_message("err_username_unavailable", 2)
                        Server.send_message(self, cl_soc, m)
                        cl_soc.close()
                        break

                    else:
                        # else The server allows the user to join the chat.
                        # and add the client to clients list
                        self.client_info[user_name] = ar
                        print(f"{li[0]}: {user_name}")

                except Exception as e:
                    print(e, Exception)

            # if the message is request_users_list:
            elif m == "request_users_list":
                user = Server.get_username(self, cl_soc)
                print(f"request_users_list: {user}")
                # get the list of usernames in ascending order
                list_usernames = [x for x in self.client_info.keys()]
                list_usernames.sort()
                num_users = len(list_usernames)
                usernames_string = " ".join(list_usernames)
                usernames_string = f"{num_users} "+usernames_string
                # send the response users list message
                msg = util.make_message(
                    "response_users_list", 3, usernames_string)
                Server.send_message(self, cl_soc, msg)

            elif "disconnect" in m:
                # server recieves disconnect message from client
                cl_soc.close()
                li = m.split(" ")
                user = li[1]  # get user name
                # remove the user from its list of online users
                self.client_info.pop(user)
                print(f"disconnected: {user}")
                client_running = False
                break

            elif "send_file" in m:
                user = Server.get_username(self, cl_soc)
                print(f"file: {user}")
                # get the list of recipients in the message
                li = m.split(" ")
                num_recipient = int(li[1])
                list_usernames = li[2:2+num_recipient]

                # keep track of the recipients who are actually clients
                actual_username = []
                for x in list_usernames:
                    if x in self.client_info.keys():
                        # if recipient is a client, add it to the actual clients list
                        actual_username.append(x)
                    else:
                        # else if recipient not in client list then print error message
                        print(f"file: {user} to non-existent user {x}")

                for x in set(actual_username):
                    # for each actual recipient
                    # get its socket and send message
                    soc = Server.get_socket(self, x)

                    msg = li[2+num_recipient:]
                    msg = " ".join(msg)
                    # append the sender username to the message
                    msg = f"{user} "+msg
                    msg = util.make_message("forward_file", 4, msg)
                    Server.send_message(self, soc, msg)

            elif "send_message" in m:
                # if the client wants to send message
                user = Server.get_username(self, cl_soc)
                print(f"msg: {user}")
                # get the list of recipients in the message
                li = m.split(" ")
                num_recipient = int(li[1])
                list_usernames = li[2:2+num_recipient]
                message = li[2+num_recipient:]
                message = " ".join(message)

                # keep track of the recipients who are actually clients
                actual_list_usernames = []
                # check if each recipient correspond to a client
                for x in list_usernames:
                    if x in self.client_info.keys():
                        # if recipient is a client, add it to the actual clients list
                        actual_list_usernames.append(x)
                    else:
                        # else if recipient not in client list then print error message
                        print(f"msg: {user} to non-existent user {x}")

                        # remove duplicate recipients
                for x in set(actual_list_usernames):
                    # for each actual recipient
                    # get its socket and send message
                    soc = Server.get_socket(self, x)
                    # append the sender username to the message
                    mg = f"{user} "+message
                    mg = util.make_message("forward_message", 4, mg)
                    Server.send_message(self, soc, mg)

            elif m == "":
                continue
            else:
                # else if the server recieves unknown message
                m = util.make_message("err_unknown_message", 2)
                Server.send_message(self, cl_soc, m)
                Server.close_soc(self, cl_soc)
                print(
                    f"disconnected: {Server.get_username(self,cl_soc)} sent unknown command")
                break

    def get_socket(self, name):
        # returns the socket for a client's name
        for x, y in self.client_info.items():
            if x == name:
                return y[0]


# Do not change this part of code
if __name__ == "__main__":
    def helper():
        '''
        This function is just for the sake of our module completion
        '''
        print("Server")
        print("-p PORT | --port=PORT The server port, defaults to 15000")
        print("-a ADDRESS | --address=ADDRESS The server ip or hostname, defaults to localhost")
        print("-h | --help Print this help")

    try:
        OPTS, ARGS = getopt.getopt(sys.argv[1:],
                                   "p:a", ["port=", "address="])
    except getopt.GetoptError:
        helper()
        exit()

    PORT = 15000
    DEST = "localhost"

    for o, a in OPTS:
        if o in ("-p", "--port="):
            PORT = int(a)
        elif o in ("-a", "--address="):
            DEST = a

    SERVER = Server(DEST, PORT)
    try:
        SERVER.start()
    except (KeyboardInterrupt, SystemExit):
        exit()
