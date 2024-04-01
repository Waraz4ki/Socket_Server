import sys
import os

import logging
import socket
import json

PORT = 60_000
HOST = "127.0.0.1"

password = "1234"

def init_server(host=str, port=int):
    with socket.socket(socket.AF_INET, type=socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen()
        conn, addr = server.accept()
        with conn:
            print(f"Connected by {addr}")
            
            if conn.recv(1026).decode() == password:
                while True:
                    recieved = conn.recv(1026)
                    if recieved:
                        print(recieved.decode())
                    else:
                        pass
            else:
                conn.close()
    
init_server(HOST,PORT)
        