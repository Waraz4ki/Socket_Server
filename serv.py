from core.asocket import AServer
from core.utils.Handlers import *
import socket
import time

PORT = 60_000
HOST = socket.gethostbyname(socket.gethostname())

Server = AServer(HOST, PORT, [ChatHandler,FFTHandler])
Server.activate()
Server.recieve_connections()
