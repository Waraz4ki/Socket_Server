from core.asocket import AServer, ASocket
from core.utils.Handlers import *
import socket
import time

PORT = 60_000
HOST = socket.gethostbyname(socket.gethostname())

print(HOST)

Server = AServer(ASocket(), HOST, PORT, [ChatHandler,FFTHandler])
Server.activate()
Server.recieve_connections()
