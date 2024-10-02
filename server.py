from core.asocket import AServer, ASocket, Connection_Framework
from core.utils.Handlers import * 
from core.utils.Protocols import *
import socket
import time

PORT = 60_000
HOST = socket.gethostbyname(socket.gethostname())

Server = AServer(Connection_Framework(), HOST, PORT, [ChatHandler, FFTHandler, PlaceholderHandler, ChatProtocol, FFTProtocol, PlaceholderProtocol])
Server.activate(backlog=2)
Server.recieve_connections()
