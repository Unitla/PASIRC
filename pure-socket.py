import socket, ssl

HOST = 'nefro.tk'
PORT = 8000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.verify_mode = ssl.CERT_REQUIRED
context.load_verify_locations('./certs/ca/ca.crt')
context.load_cert_chain(certfile='./certs/client/client.crt', keyfile="./certs/client/client.key")
if ssl.HAS_SNI:
    secure_sock = context.wrap_socket(sock, server_hostname=HOST)
else :
    secure_sock = context.wrap_socket(sock)
cert = secure_sock.getpeercert()
if not cert or ssl.match_hostname(cert, HOST):
    raise Exception("Error" )
secure_sock.send(" ... ")
secure_sock.close()
sock.close()