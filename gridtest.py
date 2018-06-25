import sys,threading,socket,ssl
import Tkinter as tk

HOST = 'nefro.tk'
PORT = 6666


def recv_all(sock, crlf):
        data = ""
        while not data.endswith(crlf):
                data = data + sock.read(1)
        return data

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations('cert.pem')
#context.load_cert_chain(certfile='./certs/client/client.crt', keyfile="./certs/client/client.key")
if ssl.HAS_SNI:
    secure_sock = context.wrap_socket(sock, server_hostname=HOST)
else :
    secure_sock = context.wrap_socket(sock)
cert = secure_sock.getpeercert()
if not cert or ssl.match_hostname(cert, HOST):
    raise Exception("Error" )
secure_sock.send("LOGIN:admin@haslo")
print recv_all(secure_sock, "\r\n")
secure_sock.send("ME:root")
#secure_sock.close()
#sock.close()

class Window():
    def window(self):
        mGui = tk.Tk()
        mGui.title("Log-In")

        command = tk.Entry(mGui)
        command.pack()
        button = tk.Button(mGui, text="push command", width=25, command=lambda: self.click(command.get()))
        button.pack()
        secure_sock.send("LIST:")
        mGui.mainloop()

    def click(self,message):
        secure_sock.send(message)

    def loop(self):
        while True:
            data = secure_sock.recv(1024)
            if data:
                print data


w = Window()
ts1 = threading.Thread(target = w.window)
ts2 = threading.Thread(target = w.loop)
ts1.run()
ts2.run()

ts1.join()
ts2.join()
