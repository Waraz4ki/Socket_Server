from core.asocket import AClient, ASocket, Connection_Framework
from core.utils.Protocols import *
from core.utils.Handlers import *
import socket

PORT =50_000
HOST = "192.168.178.108"

Client = AClient(Connection_Framework(), HOST, PORT, PlaceholderProtocol)
Client.connect()
Client.setup()
Client.handle()
