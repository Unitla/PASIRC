import Tkinter as tk
import os
import socket, ssl
import hashlib, threading
from encodings import utf_8
from re import U
import sys
from time import sleep

reload(sys)  # Reload does the trick!
sys.setdefaultencoding('UTF8')

nick = ""
roomlist = ["one", "tlistLabelo", "three", "four"]
users = ""

HOST = 'nefro.tk'
PORT = 6666

current_room = 'default'


def recv_all(sock, crlf):
    data = ""
    while not data.endswith(crlf):
        data = data + sock.read(1)
    return data

    # Functions command returns command string in expected format


# LOGIN:nick@haslo - login/register user with name nick
def command_login(login, password):
    if login != 'root':
        password = hashlib.md5(password).hexdigest()
    return ''.join(["LOGIN:", login, "@", password, "\r\n"])


# JOIN:room_name - join room
def command_join(your_nick, room_name):
    print "my roomname : " + room_name
    global current_room
    current_room = room_name
    return ''.join(["JOIN:", your_nick, "@", room_name, "\r\n"])


# KICK:yournick:nick - disconnect user with name nick
def command_kick(your_nick, kick_nick):
    return ''.join(["KICK:", your_nick, "@", kick_nick, "\r\n"])


# BAN:yournick:nick - disconnect and pernamently ban usr with name nick
def command_ban(your_nick, ban_nick):
    return ''.join(["BAN:", your_nick, "@", ban_nick, "\r\n"])


# CREATE:yournick:room_name - create room with name room_name
def command_create(your_nick, new_room_name):
    roomlist.append(new_room_name)
    return ''.join(["CREATE:", your_nick, "@", new_room_name, "\r\n"])


# DELETE:yournick:room_name - delete room with name room_name
def command_delete(your_nick, room_to_delete):
    if room_to_delete in roomlist:
        index = roomlist.index(room_to_delete)
        roomlist.pop(index)
    return ''.join(["DELETE:", your_nick, "@", room_to_delete, "\r\n"])


# ME:yournick - get info about yourself
def command_me(your_nick):
    return ''.join(["ME:", your_nick, "\r\n"])


# LIST - get rooms list
def command_list():
    return ''.join(["LIST:", "\r\n"])


# MSG:yournick@message - send message in courent room
def command_message(your_nick, message):
    return ''.join(["MSG:", your_nick, "@", current_room, "@", message, '\r\n'])


# USERS: - get all users
def command_users():
    return ''.join(["USERS:", "\r\n"])


# QUIT: - quit chat
def command_quit():
    global nick
    return ''.join(["QUIT:", nick, "\r\n"])


# PRIV:yournick@nick@message - send private message to user nick
def command_priv(priv_nick, message):
    global nick
    return ''.join(["PRIV:", nick, "@", priv_nick, "@", message, "\r\n"])


# GLOBAL:yournick@message - send message to all users, require at least 1 level permission
def command_global(your_nick, message):
    return ''.join(["GLOBAL:", your_nick, "@", message, '\r\n'])


# PERM:yournick@nick - rise permissions of user nick to 1 level
def command_perm(your_nick, up_nick):
    return ''.join(["PERM:", your_nick, "@", up_nick, '\r\n'])


try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations('cert.pem')
    # context.load_cert_chain(certfile='./certs/client/client.crt', keyfile="./certs/client/client.key")
    if ssl.HAS_SNI:
        secure_sock = context.wrap_socket(sock, server_hostname=HOST)
    else:
        secure_sock = context.wrap_socket(sock)
    cert = secure_sock.getpeercert()
    if not cert or ssl.match_hostname(cert, HOST):
        raise Exception("Error")
except Exception as err:
    mGuiClose = tk.Tk()
    mGuiClose.eval('tk::PlaceWindow %s center' % mGuiClose.winfo_pathname(mGuiClose.winfo_id()))
    mGuiClose.title("Error")
    mlabel = tk.Label(text="Socket connection could not be made, error code " + str(err.args[0]))
    mlabel.pack()
    mGuiClose.mainloop()
    quit(1)

# secure_sock.send("LOGIN:admin@haslo")
# print recv_all(secure_sock, "\r\n")

mGui = tk.Tk()
mGui.eval('tk::PlaceWindow %s center' % mGui.winfo_pathname(mGui.winfo_id()))
mGui.title("Log-In")

mlabel = tk.Label(text="Login").grid(row=0, column=0, sticky=tk.W)
mlabel2 = tk.Label(text="Haslo").grid(row=1, column=0, sticky=tk.W)

input_login = tk.Entry(mGui)
input_login.grid(row=0, column=1, sticky=tk.W)
input_password = tk.Entry(mGui)
input_password.grid(row=1, column=1, sticky=tk.W)


def get_users_to_list():
    secure_sock.send(command_users())
    response_data = recv_all(secure_sock, "\r\n")
    print response_data
    global users
    users = response_data[5:-4].replace('\'', '').replace(' ', '').split(',')
    print users


def get_rooms_to_list():
    secure_sock.send(command_list())
    response_data = recv_all(secure_sock, "\r\n")
    global roomlist
    roomlist = response_data[5:-4].replace('\'', '').replace(' ', '').split(',')
    print roomlist


def log_in(login, password):
    secure_sock.send(command_login(login, password))
    response_data = recv_all(secure_sock, "\r\n")
    print response_data
    if "200" in response_data or "201" in response_data:
        global nick
        nick = login
        mGui.destroy()
        get_rooms_to_list()
        get_users_to_list()
    else:
        quit()


button_login = tk.Button(text="Log in", command=lambda: log_in(input_login.get(), input_password.get())).grid(row=2,
                                                                                                              column=0,
                                                                                                              sticky=tk.W)

mGui.mainloop()


def insert_message(window, input_command):
    global nick
    window.text.config(state='normal')
    # if input sterts with / is recognised as command
    if input_command != '' and input_command[0] == '/':
        # take command name
        if " " in input_command:
            command = input_command.split(" ", 1)
            if command[0] == '/join':
                result = ''.join(command_join(nick, command[1]))
            elif command[0] == '/message':
                result = ''.join(command_message(nick, command[1]))
            elif command[0] == '/kick':
                result = ''.join(command_kick(nick, command[1]))
            elif command[0] == '/ban':
                result = ''.join(command_ban(nick, command[1]))
            elif command[0] == '/delete':
                result = ''.join(command_delete(nick, command[1]))
            elif command[0] == '/create':
                result = ''.join(command_create(nick, command[1]))
            elif command[0] == '/global':
                result = ''.join(command_global(nick, command[1]))
            elif command[0] == '/perm':
                result = ''.join(command_perm(nick, command[1]))
            elif command[0] == '/login':
                command = input_command.split(" ")
                nick = command[1]
                print nick
                password = command[2]
                print password
                result = ''.join(command_login(nick, password))
                print result
            else:
                result = None
        else:
            command = [input_command]
            if command[0] == '/me':
                result = ''.join(command_me(nick))
            elif command[0] == '/list':
                result = ''.join(command_list())
            elif command[0] == '/quit':
                window.button.destroy()
                result = ''.join(command_quit())
            elif command[0] == '/users':
                result = ''.join(command_users())
            else:
                result = None

        # check if there was a command match
        if result is None:
            window.write("Command %s not found \n" % (command[0]))
        else:
            window.write("Command %s found \n" % (result))
            secure_sock.send(result)
            w.commantLine.delete(0, 'end')
    elif input_command != '':
        window.write("Message %s \n" % (input_command))
        result = ''.join(command_message(nick, input_command))
        secure_sock.send(result)
        w.commantLine.delete(0, 'end')


class UserWindow():
    # create a Tk root listLabelidget

    def disconnect(self):
        insert_message(self, "/quit")
        self.root.destroy()

    def window(self):
        self.root = tk.Tk()
        x = (self.root.winfo_screenwidth() - self.root.winfo_reqwidth()) / 2 - 250
        y = (self.root.winfo_screenheight() - self.root.winfo_reqheight()) / 2 - 250
        self.root.geometry("+%d+%d" % (x, y))
        self.root.title("mIrc Chat")

        # first parametr - parent listLabelindolistLabel
        listLabel = tk.Label(self.root, text="Lista Pokoi")
        listLabel.grid(row=0, column=0, sticky=tk.W)
        # pack - fit the size of the listLabelindolistLabel to the given text
        listLabel.pack()

        # listbox

        self.listbox = tk.Listbox(self.root)
        # listbox.grid(row=0, column=1)
        self.listbox.pack()

        # first parametr - parent listLabelindolistLabel
        messagesLabel = tk.Label(self.root, text="Wiadomosci")
        # messagesLabel.grid(row=1, column=0, sticky=tk.W)
        # pack - fit the size of the listLabelindolistLabel to the given text
        messagesLabel.pack()

        self.commantLine = tk.Entry(self.root)
        # commantLine.grid(row=1, column=1, sticky=tk.W)
        self.commantLine.pack()
        # can listLabelrite after program starts
        self.commantLine.focus()

        # lambda is used to pass parameters to function
        self.button = tk.Button(self.root, text="push command", width=25,
                                command=lambda: insert_message(self, self.commantLine.get()))
        self.button.pack()

        for item in roomlist:
            self.listbox.insert(tk.END, item)

        scrollbar = tk.Scrollbar(self.root)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.text = tk.Text(self.root, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        self.text.config(state=tk.DISABLED)
        self.text.pack()

        scrollbar.config(command=self.text.yview)

        scrollbar.pack()

        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        # self.root.protocol('WM_DELETE_WINDOW', self.disconnect())  # root is your root window
        self.is_disconnect = False
        self.root.mainloop()

    def on_exit(self):
        if not self.is_disconnect:
            insert_message(self, "/quit")
        self.exit = 0
        sleep(0.1)
        self.root.destroy()
        secure_sock.close()
        sock.close()
        os._exit(0)

    def loop(self):
        self.exit = 1
        while self.exit:
            try:
                data = recv_all(secure_sock, '\r\n')
                if data != None and ':' not in data:
                    print data
                    self.write(data)
                    print data[0], data[2]
                    if data[0] == '2':
                        if data[2] == '6':
                            self.update_list(data)
                        elif data[2] == '4' or data[2] == '5':
                            self.update_local_room_list()
                        elif data[2] == '9':
                            self.is_disconnect = True
                            insert_message(self, "/quit")
                            self.button.destroy()
                            secure_sock.close()
                            sock.close()
                            self.exit = 0
                        elif data[1] == '1':
                            if data[2] == '8':
                                self.is_disconnect = True
                                insert_message(self, "/quit")
                                self.button.destroy()
                                secure_sock.close()
                                sock.close()
                                self.exit = 0
                            elif data[2] == '0':
                                self.exit = 0
                                self.button.destroy()
                elif data != None:
                    self.write(data)
            except ssl.SSLError as err:
                print " %s %s " + str(err)
                self.write(str(err))
                self.button.destroy()
        print 'wychodze'

    def update_list(self, data):
        self.listbox.delete(0, 'end')
        roomlist = data[5:-4].replace('\'', '').replace(' ', '').split(',')
        print roomlist
        for item in roomlist:
            self.listbox.insert(tk.END, item)

    def update_local_room_list(self):
        self.listbox.delete(0, 'end')
        for item in roomlist:
            self.listbox.insert(tk.END, item)

    def write(self, data):
        self.text.config(state='normal')
        self.text.insert('end', "%s\n" % (data))
        self.text.yview(tk.END)
        self.text.config(state='disabled')


w = UserWindow()
ts1 = threading.Thread(target=w.window)
ts2 = threading.Thread(target=w.loop)
ts1.start()
ts2.start()

ts1.join()
ts2.join()
