from asocket import AClient
from utils.Protocols import ChatProtocol, FFTProtocol
from utils.Handlers import ChatHandler, FFTHandler
import mmap

PORT = 60_000
HOST = "192.168.178.108"

Client = AClient(HOST, PORT, FFTProtocol)
Client.connect()