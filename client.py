#!/usr/bin/env python
import socket, ssl

def recv_all(sock, crlf):
        data = ""
        while not data.endswith(crlf):
                data = data + sock.read(1)
        return data

HOST = 'nefro.tk'
PORT = 6666
SERVER = (HOST, PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(SERVER)

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations('cert.pem')

if ssl.HAS_SNI:
        secure_sock = context.wrap_socket(sock, server_hostname=HOST)
else :
        secure_sock = context.wrap_socket(sock)

cert = secure_sock.getpeercert()
print cert

if not cert or ssl.match_hostname(cert, HOST):
        raise Exception("Error hostnames do not match" )

print recv_all(secure_sock, "\r\n")
secure_sock.write("LOGIN:root@root\0")
print recv_all(secure_sock, "\r\n")

#secure_sock.write("exit \r\n")
#print recv_all(secure_sock, "\r\n")

secure_sock.close()
sock.close()
