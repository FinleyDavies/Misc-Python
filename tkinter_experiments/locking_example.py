import threading
class Test:
    def __init__(self):
        self._lock = threading.Lock()

    def method1(self):
        print("acquiring lock")
        with self._lock:
            print("method1")
            self.do_stuff()
            self.method2()

    def method2(self):
        print("acquiring lock")
        with self._lock:  # <-- lock can never be acquired
            print("method2")
            self.do_stuff()

    def do_stuff(self):
        pass

if __name__ == "__main__":
    t = Test()
    t.method1()
