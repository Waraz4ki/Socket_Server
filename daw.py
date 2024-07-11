from core.asocket import AClient, ASocket
from core.utils.Protocols import ChatProtocol, FFTProtocol
from core.utils.Handlers import ChatHandler, FFTHandler
import socket

PORT = 60_000
HOST = "192.168.56.1"

Client = AClient(ASocket(), HOST, PORT, ChatProtocol)
Client.connect()
Client.setup()
Client.handle()
