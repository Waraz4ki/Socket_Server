from src.server import SocketServer
from src.handler import BaseHandler

import time

PORT = 60_000
HOST = "192.168.178.108"


class TestHandle(BaseHandler):
    def __init__(self) -> None:
        super().__init__()
        
    def test(self, data):
        print(data)

if __name__ == "__main__":
    Server = SocketServer(HOST, PORT, TestHandle)
    Server.activate()