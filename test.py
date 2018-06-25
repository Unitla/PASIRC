import Tkinter as tk
import socket, ssl
import hashlib

nick = ""
roomlist = ["one", "tlistLabelo", "three", "four"]
users = ""

HOST = 'nefro.tk'
PORT = 6666


def recv_all(sock, crlf):
    data = ""
    while not data.endswith(crlf):
        data = data + sock.read(1)
    return data

    # Functions command returns command string in expected format


# LOGIN:nick@haslo - login/register user with name nick
def command_login(login, password):
    password = hashlib.md5(password).hexdigest()
    return ''.join(["LOGIN:", login, "@", password])


# JOIN:room_name - join room
def command_join(your_nick, room_name):
    print "my roomname : " + room_name
    return ''.join(["JOIN:", your_nick, "@", room_name])


# KICK:yournick:nick - disconnect user with name nick
def command_kick(your_nick, kick_nick):
    return ''.join(["KICK:", your_nick, "@", kick_nick])


# BAN:yournick:nick - disconnect and pernamently ban usr with name nick
def command_ban(your_nick, ban_nick):
    return ''.join(["BAN:", your_nick, ":", ban_nick])


# CREATE:yournick:room_name - create room with name room_name
def command_create(your_nick, new_room_name):
    return ''.join(["CREATE:", your_nick, "@", new_room_name])


# DELETE:yournick:room_name - delete room with name room_name
def command_delete(your_nick, room_to_delete):
    return ''.join(["DELETE:", your_nick, "@", room_to_delete])


# ME:yournick - get info about yourself
def command_me(your_nick):
    return ''.join(["ME:", your_nick])


# LIST - get rooms list
def command_list():
    return ''.join(["LIST:", '\0'])


# MSG:yournick@message - send message in courent room
def command_message(your_nick, message):
    return ''.join(["MSG:", your_nick, "@", message, '\0'])


# USERS: - get all users
def command_users():
    return ''.join(["USERS:"])


def command_quit():
    return ''.join(["QUIT:", nick])


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

mGui = tk.Tk()
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


def insert_message(input_command):
    global nick
    text.config(state='normal')
    # if input sterts with / is recognised as command
    if (input_command[0] == '/'):
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
                result = ''.join(command_quit())
            elif command[0] == '/users':
                result = ''.join(command_users())
            else:
                result = None

        # check if there was a command match
        if result is None:
            text.insert('end', "Command %s not found \n" % (command[0]))
        else:
            text.insert('end', "Command %s found \n" % (result))
            secure_sock.send(result)
            response_data = recv_all(secure_sock, "\r\n")
            print response_data
            text.insert('end', "Response : %s  \n" % (response_data))
    else:
        text.insert('end', "Message %s \n" % (input_command))
    text.config(state='disabled')


# create a Tk root listLabelidget
root = tk.Tk()
root.title("mIrc Chat")

# first parametr - parent listLabelindolistLabel
listLabel = tk.Label(root, text="Lista Pokoi")
listLabel.grid(row=0, column=0, sticky=tk.W)
# pack - fit the size of the listLabelindolistLabel to the given text
listLabel.pack()

# listbox

listbox = tk.Listbox(root)
# listbox.grid(row=0, column=1)
listbox.pack()

# first parametr - parent listLabelindolistLabel
messagesLabel = tk.Label(root, text="Wiadomosci")
# messagesLabel.grid(row=1, column=0, sticky=tk.W)
# pack - fit the size of the listLabelindolistLabel to the given text
messagesLabel.pack()

commantLine = tk.Entry(root)
# commantLine.grid(row=1, column=1, sticky=tk.W)
commantLine.pack()
# can listLabelrite after program starts
commantLine.focus()

# lambda is used to pass parameters to function
button = tk.Button(root, text="push command", width=25, command=lambda: insert_message(commantLine.get()))
button.pack()

for item in roomlist:
    listbox.insert(tk.END, item)

scrollbar = tk.Scrollbar(root)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text = tk.Text(root, wrap=tk.WORD, yscrollcommand=scrollbar.set)
text.config(state=tk.DISABLED)
text.pack()

scrollbar.config(command=text.yview)

scrollbar.pack()


def recv_all(sock, crlf):
    data = ""
    while not data.endswith(crlf):
        data = data + sock.read(1)
    return data


def disconnect():
    insert_message("/quit")
    root.destroy()


root.protocol('WM_DELETE_WINDOW', disconnect)  # root is your root window

root.mainloop()
