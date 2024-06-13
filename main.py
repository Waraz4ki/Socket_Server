from core.src.server import *
import time



PORT = 60_000
HOST = "192.168.178.108"

if __name__ == "__main__":
    Server = SocketServer(HOST, PORT, ChatHandler)
    Server.activate(block_main_thread=False)
    