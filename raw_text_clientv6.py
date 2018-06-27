#!/usr/bin/env python
import socket, ssl,threading,sys

HOST = '::1'
PORT = 6666


def recv_all(sock, crlf):
        data = ""
        while not data.endswith(crlf):
                data = data + sock.read(1)
        return data

sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations('certv6.pem')
#context.load_cert_chain(certfile='./certs/client/client.crt', keyfile="./certs/client/client.key")
if ssl.HAS_SNI:
    secure_sock = context.wrap_socket(sock, server_hostname=HOST)
else :
    secure_sock = context.wrap_socket(sock)
cert = secure_sock.getpeercert()
if not cert or ssl.match_hostname(cert, HOST):
    raise Exception("Error" )

login = raw_input('pass login ')
password = raw_input('pass password ')

login_seq= ''.join(["LOGIN:",login,"@",password,"\r\n"])

secure_sock.send(login_seq)
login_response = recv_all(secure_sock,"\r\n")
print login_response

if not ("201" in login_response or "200" in login_response):
    secure_sock.close()
    sock.close()
    print "ending program"
    quit(1)

class Client():
    def loop(self):
        while 1:
            data=recv_all(secure_sock,"\r\n")
            if data:
                print data


    def get_command(self):
        while 1:
            command=raw_input("$")
            if command:
                secure_sock.send(command+"\r\n")
            if "QUIT:" in command:
                secure_sock.close()
                sock.close()
                quit(2)


client = Client()
ts1= threading.Thread(target=client.loop)
ts2= threading.Thread(target=client.get_command)

ts1.start()
ts2.start()

ts1.join()
ts2.join()
