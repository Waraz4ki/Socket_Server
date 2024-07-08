import threading

class ThreadManager(threading.Thread):
    def __init__(self):
        pass
        #self.thread_list = []
        #if not isinstance(loop_setup, function):
        #    raise TypeError(f"loop_setup has to be a function not a {type(loop_setup)}")
        #self.loop_setup = loop_setup
        
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
        #self.loop_setup()
        def wrapper(*args):
            while self.thread_list.count(threading.current_thread().name):
                func(*args)
        return wrapper
