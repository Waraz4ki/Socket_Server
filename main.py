from backend.src.server import *

import time

PORT = 60_000
HOST = "192.168.178.108"


if __name__ == "__main__":
    Server = SocketServer(HOST, PORT, FileTransferHandlerNew)
    Server.activate()