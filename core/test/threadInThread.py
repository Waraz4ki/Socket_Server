import threading
import time

class Main():
    def __init__(self) -> None:
        print(threading.current_thread())
        while True:
            threading.Thread(target=self.work).start()
        
    def work(self):
        while True:
            time.sleep(2) 
            print(threading.current_thread())
            
d = Main()
threading.Thread(target=d.__init__()).start()
