from asocket import AServer
from utils.Protocols import ChatProtocol, FFTProtocol
from utils.Handlers import FFTHandler, ChatHandler

PORT = 60_000
HOST = "192.168.178.108"

Server = AServer(HOST, PORT)
Server.activate()
Server.recieve_connections()