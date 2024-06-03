import os
import time

def list_files(dir):
    r = []
    subdirs = [x[0] for x in os.walk(dir)]
    print(subdirs)
    time.sleep(2)
    
    for subdir in subdirs:
        files = os.walk(subdir).__next__()[2]
        print(files)
        time.sleep(1)
        
        if (len(files) > 0):     
            for file in files:
                r.append(os.path.join(subdir, file))
    return r

def cylcedir(path):
    for entry in os.scandir(path):
        dir = entry
        
        if dir.is_dir():
            print(f"Folder: {dir.name}")
            time.sleep(2)
            
            for entry2 in os.scandir(dir.path):
                if entry2.is_file():
                    print(entry2.name)
                    time.sleep(1)
                    
                elif entry2.is_dir():
                    print("F")
                    print()
                    dir = entry2
                    
        elif dir.is_file():
            print(f"File: {dir.name}")
            time.sleep(1)
            
    def loop(self, path):
        for dir in os.scandir(path):
            if dir.is_dir():
                print(f"Folder:{dir.name}")
                self.conn.send(b"Folder:"+dir.name.encode())
                
                self.loop(dir.path)
                
            elif dir.is_file():
                print(f"File:{dir.name}")
                self.conn.send(b"File:"+dir.name.encode())
                
                time.sleep(1)
                
                with open(file=dir, mode="rb") as file:
                    self.conn.sendfile(file)