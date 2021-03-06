import socket, ssl

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
else:
    secure_sock = context.wrap_socket(sock)
cert = secure_sock.getpeercert()
if not cert or ssl.match_hostname(cert, HOST):
    raise Exception("Error" )
secure_sock.send("LOGIN:admin@haslo")
print recv_all(secure_sock, "\r\n")
secure_sock.send("LOGIN:admin@haslo")
print recv_all(secure_sock, "\r\n")
secure_sock.send("ME:admin")
print recv_all(secure_sock, "\r\n")
if not cert or ssl.match_hostname(cert, HOST):    raise Exception("Error" )
secure_sock.send(" ... ")
secure_sock.close()
sock.close()
