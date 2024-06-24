from asocket import AServer
from utils.Handlers import *

PORT = 60_000
HOST = "192.168.178.108"

Server = AServer(HOST, PORT, (ChatHandler, FFTHandler))
Server.activate()
Server.recieve_connections()