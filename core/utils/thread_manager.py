import threading

class ThreadManager(threading.Thread):
    def __init__(self):
        self.thread_list = []
    
    def start(self, thread_obj):
        #worker = threading.Thread(target=target, name=name, kwargs=kwargs, daemon=daemon)
        worker = thread_obj
        self.thread_list.append(worker.name)
        worker.start()
        
        return True
    
    def stop(self, worker_name:str | None=None):
        self.thread_list.remove(worker_name)
    
    def stop_all(self):
        self.thread_list.clear()
        
    def thread_loop(self, func):
        def wrapper(*args):
            while self.thread_list.count(threading.current_thread().name):
                #print(self.thread_list)
                func(*args)
        return wrapper
    
    
def thread_decorateor(func):
    def wrap(*args):
        while True:
            func(*args)
    return wrap
