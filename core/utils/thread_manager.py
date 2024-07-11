import threading

class ThreadManager(threading.Thread):
    def __init__(self):
        self.thread_list = []
        
    def start(self, thread_obj):
        worker = thread_obj
        self.thread_list.append(worker.name)
        worker.start()
        
        return True
    
    def stop(self, worker_name:str | None=None):
        self.thread_list.remove(worker_name)
    
    def stop_current(self):
        self.thread_list.remove(threading.current_thread().name)
    
    def stop_all(self):
        self.thread_list.clear()
        
    def thread_loop(self, func):
        def wrapper(*args):
            while self.thread_list.count(threading.current_thread().name):
                func(*args)
        return wrapper
