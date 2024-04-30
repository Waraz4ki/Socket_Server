import logging
import socket
import json
import threading

logger = logging.getLogger(__name__)
logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)

PORT = 60_000
HOST = "192.168.178.108"


chat = {
    "handle" : "chat",
}

class Socketclient:
    def __init__(self, host=str, port=int):
        self.host = host
        self.port = port
        
        self.connection = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        
    def connect(self, form):
        self.connection.connect((self.host, self.port))
        self.on_connect(form)
        
        while True:
            raw = input(">>>")
            self.connection.send(raw.encode())
    
    def on_connect(self, form):
        self.send_form(form)
            
    def send_form(self, form):
        self.connection.send(form)
        pass

client = Socketclient(HOST, PORT)
client.connect(b"test")
