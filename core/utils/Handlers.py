#from asocket import ASocket
from utils.base import Base
from os import path, makedirs
    
class ChatHandler(Base):
    def handle(self):
        data = self.format_recv_msg(self.sock)
        print(f"{self.addr}: {data}")

class FFTHandler(Base):
    def setup(self):
        remote_path = input(">>>")
        self.send_msg(self.sock, remote_path)
        self.root_path = input(">>>")
    
    def handle(self):
        while True:
            package = self.format_recv_msg(self.sock)
            print(package)
            partial_path = package["path"]
            package_type = package["type"]
            name = package["name"]
            try:
                makedirs(path.join(self.root_path, partial_path))
            except FileExistsError:
                pass
            
            if package_type == "folder":
                absolute_path = path.join(self.root_path, partial_path, name)
                makedirs(absolute_path)
                self.send_msg(self.sock, True)
            
            if package_type == "file":
                absolute_path = path.join(self.root_path, partial_path, name)
                self.send_msg(self.sock, True)
                
                with open(file=absolute_path, mode="wb+") as file:
                    while True:
                        #print("LOOP")
                        chunck = self.format_recv_msg(self.sock)
                        if chunck == 200 or chunck is None:
                            print("EXIT")
                            break
                        file.write(chunck)
