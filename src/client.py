import logging
import socket
import json

logger = logging.getLogger(__name__)
logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)

PORT = 60_000
HOST = "192.168.178.108"

class Socketclient:
    def __init__(self, host, port) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            print(s.recv(1253))
            s.send(input("").encode())
            
            while True:
                
                raw = input(">>>")
                s.send(raw.encode())

client = Socketclient(HOST, PORT)