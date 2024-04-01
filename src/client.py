import sys
import os

import logging
import socket
import json

PORT = 60_000
HOST = "127.0.0.1"

def connect(host=str, port=int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        while True:
            raw = input(">>>")
            s.send(raw.encode())

connect(HOST, PORT)