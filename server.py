#!/usr/bin/env python

import socket, threading, ssl
import sys
# sys.setdefaultencoding() does not exist, here!
reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

KEYFILE = 'key.pem'
CERTFILE = 'cacert.pem'
head_split = ":"
login_split = "@"
message_split = "@"
crlf = "\r\n"
users = [ {"name": "root", "password": "root", "permisions": 0 } ]
#rooms = [ {"name": "default", "1" : "root"} ]
clients ={ }
rooms = {"default": []}

def parse_recvd_data(data,split):

  parts = data.split(split)
  head = parts[:-1]
  rest = parts[-1]
  return (head, rest)


def check_head(data,sock):

        (head, rest) = parse_recvd_data(data,head_split)
        if head[0] == "LOGIN":
                return add_user(rest)
        elif head[0] == "QUIT":
                return (210,"User disconnected")
        elif head[0] == "LIST":
                return get_rooms_list()
        elif head[0] == "MSG":
                return send_msg_room(rest)
        elif head[0] == "ME":
                return user_info(rest)
        elif head[0] == "CREATE":
                return create_room(rest,sock)
        elif head[0] == "DELETE":
                return delete_room(rest,sock)
        elif head[0] == "JOIN":
                return join_room(rest,sock)
        elif head[0] == "KICK":
                return kick(rest,sock)
        elif head[0] == "USERS":
                return get_all_users()
        elif head[0] == "PRIV":
                return send_priv(rest)
        elif head[0] == "GLOBAL":
                return send_message_global(rest)
        elif head[0] == "PERM":
                return add_permision(rest)
        elif head[0] == "BAN":
                return ban(rest)
        else:
                return (100, "Command not found")

def add_user(data):
        (login, password) = parse_recvd_data(data,login_split)
        results = filter(lambda user: user['name'] == login[0], users)
        if not results:
                new_user = {"name": login[0], "password": password, "permisions": 2}
                users.append(new_user)
                #print users
                return (200, "User added")
        else:
                if password == results[0]['password']:
                        print "user authorized"

                        return (201, "User authorized")
                else:
                        print "wrong password"
                        #print results[0][password]
                        return (101, "Wrong password")
def user_info(login):
        results = filter(lambda user: user['name'] == login, users)
        if not results:
                #print login
                return (102, "No user")
        return (202, str(results))

def send_message_global(data):
        (nick, message) = parse_recvd_data(data,message_split)
        (login, rest) = parse_recvd_data(data,login_split)
        results = filter(lambda user: user['name'] == login[0], users)
        if results[0]['permisions'] >= 2:
                return (107, "Insufficient premision to send global message")
        else:
                for item in clients:
                        item.sendall("214 GLOBAL MESSAGE: "+message + crlf)
                return (212, "Global messaged send")

def send_msg_room(data):
        (log, message) = parse_recvd_data(data,message_split)
        print log
        print message
        print log[0]
        print log[1]
        print rooms
        #print list(rooms[log[1]])
        for item in list(rooms[log[1]]):
                item.sendall(log[0]+ ": "+ message + crlf)
        return (203, "Message send")

def update_clients(connection, data):
        (login, rest) = parse_recvd_data(data,login_split)
        rooms['default'].append(connection)
        #print rooms
        clients[connection] = login[0]

def create_room(data,sock):
        (login, rest) = parse_recvd_data(data,login_split)
        results = filter(lambda user: user['name'] == login[0], users)
        if results[0]['permisions'] >= 2:
                return (103, "Insufficient premision to create room ")

        else:
                clean_client(sock)
                socket = clients.keys()[clients.values().index(login[0])]
                lis = list()
                lis.append(socket)
                rooms[rest] = lis
                print "------"
                print rooms
                print "------"
                return (204, "Room suceffully created")

def delete_room(data,sock):
        (login, rest) = parse_recvd_data(data,login_split)
        results = filter(lambda user: user['name'] == login[0], users)
        if results[0]['permisions'] >= 2:
                return (104, "Insufficient premision to delete room")
        else:
                clean_client(sock)
                rooms['default'].append(sock)
                del rooms[rest]
                return (205, "Room deleted")
def get_rooms_list():
        list_of_rooms = rooms.keys()
        return (206, str(list_of_rooms))

def join_room(data,sock):
        (login, rest) = parse_recvd_data(data,login_split)
        #results = filter(lambda socket: socket['name'] == login[0], clients)
        list_of_rooms = rooms.keys()
        if rest not in list_of_rooms:
                return (105, "Room doesn't exist")
        else:
                clean_client(sock)
                socket = clients.keys()[clients.values().index(login[0])]
                #lis= rooms[rest]
                lis=list()
                for item in rooms[rest]:
                        lis.append(item)
                lis.append(socket)
                rooms[rest] = lis

                print rooms
                return (207, "Successfully joined")

def kick(data):
        (nick, rest) = parse_recvd_data(data,login_split)
        socket = clients.keys()[clients.values().index(rest)]
        results = filter(lambda user: user['name'] == nick[0], users)
        if results[0]['permisions'] >= 2:
                return (106, "Insufficient permission to kick")
        else:
                results = filter(lambda user: user['name'] == rest, users)
                if len(results) == 0:
                        return (112, "User not found")
                else:
                        socket.sendall(str("209 You have been kicked"))
                        socket.close()
                        clean_client_all(socket)
                        return (208, "User have been successfully kicked")

def ban(data):
        (nick, rest) = parse_recvd_data(data,login_split)
        socket = clients.keys()[clients.values().index(rest)]
        results = filter(lambda user: user['name'] == nick[0], users)
        if results[0]['permisions'] >= 2:
                return (110, "Insufficient permission to ban")
        else:
                results = filter(lambda user: user['name'] == rest, users)
                if len(results) == 0:
                        return (111, "User not found")
                else:
                        index = users.index(results[0])
                        results[0]['password'] = "\x00\x00\x00"
                        clean_client(socket)
                        users[index] = results[0]
                        socket.sendall(str("218 You have been banned"))
                        socket.close()
                        return (217, "User have been successfully banned")


def get_all_users():
        list = clients.values()
        return (211, str(list))

def send_priv(data):
        (login, rest) = parse_recvd_data(data,login_split)
        socket = clients.keys()[clients.values().index(login[1])]
        socket.sendall(str("212 private message from: "+login[0]+ " : "+ rest))
        return (213, "Private message have been send")

def add_permision(data):
        (nick, rest) = parse_recvd_data(data,login_split)
        results = filter(lambda user: user['name'] == nick[0], users)
        if results[0]['permisions'] != 0:
                return (108, "Insufficient permission to upgrade permisions")
        else:
                results = filter(lambda user: user['name'] == rest, users)
                if len(results) == 0:
                        return (109, "User not found")
                else:
                        index = users.index(results[0])
                        results[0]['permisions'] = 1
                        users[index] = results[0]
                        return (216, "Permisions successfully upgraded" )
def clean_client(sock):
        for item in rooms:
                print rooms[item]
                if sock in rooms[item]:
                        del rooms[item][rooms[item].index(sock)]

def clean_client_all(sock):
        for item in rooms:
                print rooms[item]
                if sock in rooms[item]:
                        del rooms[item][rooms[item].index(sock)]

        del clients[sock]


def send_code(socket, code, message):
        socket.sendall(str(code)+" "+message+" "+crlf)

class ClientThread(threading.Thread):
    def __init__(self, connection):
        threading.Thread.__init__(self)
        self.connection = connection

    def run(self):
        while True:
            data = self.connection.recv(8192)
            if data:
                if data.startswith('exit'):
                        break
                data = data[:-2]
                (head, rest) = parse_recvd_data(data,head_split)
                print data
                print head[0]
                print rest
                #print check_head(data)
                (code, message) = check_head(data,self.connection)
                print clients
                #print self.connection
                send_code(self.connection,code,message)
                if (code == 101) or (code == 210):
                        break
                elif (code == 200) or (code == 201):
                        update_clients(self.connection, rest)
            else:
                break
        #delete all junk sockets in rooms etc
        print "close"
        clean_client_all(self.connection)
        self.connection.close()


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.address = (self.ip, self.port)
        self.server = None


    def run(self):
        try:

            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(self.address)
            self.server.listen(5)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            ssl_sock = ssl.wrap_socket(self.server, keyfile=KEYFILE, certfile=CERTFILE, server_side=True, ssl_version=ssl.PROTOCOL_TLSv1_2)

            while True:

                #connection, (ip, port) = self.server.accept()
                connection, (ip, port) = ssl_sock.accept()
                client = (ip, port);
                print client

                #clients.append(client)
                #print connection
                #clients.append(connection)
                clients[connection] = ""
                c = ClientThread(connection)
                c.start()

        except socket.error, e:

            if self.server:
                print e
                self.server.close()
            sys.exit(1)


if __name__ == '__main__':

    s = Server('nefro.tk', 6666)

    s.run()
