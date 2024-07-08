import mmap
import os
from pathlib import Path
from core.utils.base import Base

class ChatProtocol(Base):
    def handle(self):
        data = input(">>>")
        self.package["data"] = data
        self.sock.send_msg(obj=self.package)

class FFTProtocol(Base):
    def setup(self):
        self.buffer = 100000
        
        self.path_to_copy = self.sock.format_recv_msg()
        try:
            os.scandir(self.path_to_copy)
        except FileNotFoundError:
            self.send_msg(self.sock, FileNotFoundError)
    
    def handle(self):
        self.send_dir(self.path_to_copy)
    
    def send_dir(self, current_dir):
        # loops through items in current directory
        for dir in os.scandir(current_dir):
            package = {
                "path":None,
                "type":None,
                "name":None,
            }
            split_dir = dir.path.split("\\")
            
            for i in range(len(self.path_to_copy.split("\\"))-1):
                del split_dir[0]
            split_dir.pop()
            
            package["path"] = str(Path.joinpath(Path(*split_dir)))
            package["name"] = dir.name
            
            if dir.is_dir():
                package["type"] = "folder"
                print(package)
                self.sock.send_msg(self.sock, package)
                
                if self.sock.recv_msg(self.sock):
                    self.send_dir(dir.path)
            
            if dir.is_file():
                package["type"] = "file"
                print(package)
                self.sock.send_msg(self.sock, package)
                
                if self.recv_msg(self.sock):
                    print("File Transfer Authorized...")
                    self.sock.send_file(dir.path, self.buffer)
                    
                    print("File Transfer Complete!")
                    self.sock.send_msg(self.sock, 200)
                    
