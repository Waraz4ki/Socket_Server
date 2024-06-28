from core.asocket import AClient
from core.utils.Protocols import ChatProtocol, FFTProtocol
from core.utils.Handlers import ChatHandler, FFTHandler
import socket

PORT = 60_000
HOST = "192.168.56.1"

Client = AClient(HOST, PORT, ChatProtocol)
Client.connect()
Client.handle_recursive()
