import socket, sys, threading, ssl

KEYFILE = 'key.pem'
CERTFILE = 'cert.pem'
head_split = ":"
login_split = "@"
message_split = "@"
crlf = "\r\n"
users = [ {"name": "root", "password": "root", "permisions": 0 } ]
#rooms = [ {"name": "default", "1" : "root"} ]
clients ={ }
rooms = {"default": [ ] }

def parse_recvd_data(data,split):

  parts = data.split(split)
  head = parts[:-1]
  rest = parts[-1]
  return (head, rest)


def check_head(data):

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
                return create_room(rest)
        elif head[0] == "DELETE":
                return delete_room(rest)
        elif head[0] == "JOIN":
                return join_room(rest)
        else:
                return "default"

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
                        print results[0][password]
                        return (101, "Wrong password")
def user_info(login):
        results = filter(lambda user: user['name'] == login, users)
        if not results:
                #print login
                return (102, "No user")
        return (202, str(results))

def send_message(data):
        (nick, message) = parse_recvd_data(data,message_split)
        for item in clients:
                item.sendall(nick[0]+ ": "+message + crlf)
        return (203, "Messaged send")

def send_msg_room(data):
        (nick, rest) = parse_recvd_data(data,login_split)
        (room, message) = parse_recvd_data(rest,message_split)
        print room[0]
        #print rooms[room[0]]
        #for item in rooms[room[0]]:
        #       item.sendall(nick[0]+ ": "+ message + crlf)
        return (203, "Message send")

def update_clients(connection, data):
        (login, rest) = parse_recvd_data(data,login_split)
        rooms['default'].append(connection)
        #print rooms
        clients[connection] = login[0]

def create_room(data):
        (login, rest) = parse_recvd_data(data,login_split)
        results = filter(lambda user: user['name'] == login[0], users)
        if results[0]['permisions'] >= 2:
                return (103, "Insufficient premision to create room ")
        else:
                rooms[rest] = ""
                print rooms
                return (204, "Room suceffully created")

def delete_room(data):
        (login, rest) = parse_recvd_data(data,login_split)
        results = filter(lambda user: user['name'] == login[0], users)
        if results[0]['permisions'] >= 2:
                return (104, "Insufficient premision to delete room")
        else:
                del rooms[rest]
                return (205, "Room deleted")
def get_rooms_list():
        list_of_rooms = rooms.keys()
        return (206, str(list_of_rooms))

def join_room(data):
        (login, rest) = parse_recvd_data(data,login_split)
        #results = filter(lambda socket: socket['name'] == login[0], clients)
        list_of_rooms = rooms.keys()
        if rest not in list_of_rooms:
                return (105, "Room doesn't exist")
        else:
                socket = clients.keys()[clients.values().index(login[0])]
                rooms[rest] = socket
                print rooms
                return (206, "Succeffuly joined")

def send_code(socket, code, message):
        socket.sendall(str(code)+" "+message+" "+crlf)

class ClientThread(threading.Thread):
    def __init__(self, connection):
        threading.Thread.__init__(self)
        self.connection = connection

    def run(self):
        while True:
            data = self.connection.recv(1024)
            if data:
                if data.startswith('exit'):
                        break
                (head, rest) = parse_recvd_data(data,head_split)
                print head[0]
                print rest
                #print check_head(data)
                (code, message) = check_head(data)
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
        self.connection.close()


class Server:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.address = (self.ip, self.port)
        self.server = None

    def run(self):
        try:
            self.server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.server.bind(self.address)
            self.server.listen(5)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            ssl_sock = ssl.wrap_socket(self.server, keyfile=KEYFILE, certfile=CERTFILE, server_side=True, ssl_version=ssl.PROTOCOL_TLSv1_2)

            while True:
                #connection, (ip, port) = self.server.accept()
                print ssl_sock.accept()
                connection, (ip, port,a,b) = ssl_sock.accept()
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
                self.server.close()
            print e
            sys.exit(1)


if __name__ == '__main__':
    s = Server("::1", 6666)
    s.run()
