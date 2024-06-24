#from asocket import ASocket
import mmap
import os
from pathlib import Path
from utils.base import Base
    
class ChatProtocol(Base):
    def handle(self):
        data = input(">>>")
        self.send_msg(self.sock, data)

class FFTProtocol(Base):
    def setup(self):
        self.buffer = 100000
        self.path_to_copy = self.format_recv_msg(self.sock)
        try:
            os.scandir(self.path_to_copy)
        except FileNotFoundError:
            self.send_msg(self.sock, 404)
        except TypeError:
            print("Done")
    
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
                self.send_msg(self.sock, package)
                
                if self.recv_msg(self.sock):
                    self.send_dir(dir.path)
            
            if dir.is_file():
                package["type"] = "file"
                print(package)
                self.send_msg(self.sock, package)
                
                if self.recv_msg(self.sock):
                    print("File Transfer Authorized...")
                    if os.path.getsize(dir.path) != 0:
                        # Send the contents of the file in chunks based on buffer
                        with open(dir, "rb") as file:
                            mm = mmap.mmap(file.fileno(), 0, access=mmap.ACCESS_READ)
                            
                            for i in range(0, mm.size(), self.buffer):
                                self.send_msg(self.sock, mm[i:i+self.buffer])
                            
                            mm.close()
                    print("File Transfer Complete!")
                    self.send_msg(self.sock, 200)
