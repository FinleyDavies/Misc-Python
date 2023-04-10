import threading
import tkinter
import time
from queue import Queue


class MainWindow(tkinter.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self.queue = Queue()
        self.queue_worker = QueueWorker(self.queue, self)
        self.queue_worker.start()

        self.button = tkinter.Button(self, text="send event", command=self.send_event)
        self.button.pack()

        self.label = tkinter.Label(self, text="test")
        self.label.pack()

    def send_event(self):
        self.queue.put("test")

    def update_label(self, data):
        self.label["text"] = data

    def mainloop(self, n=0):
        super().mainloop(n)
        print("joining queue worker")
        self.queue_worker.stop()


class QueueWorker(threading.Thread):
    def __init__(self, queue, app):
        super().__init__()
        self.queue = queue
        self.app = app

    def run(self):
        while True:
            print("running")
            data = self.queue.get()
            self.app.update_label(data)
            self.queue.task_done()

    def stop(self):
        self.queue.join()


if __name__ == "__main__":
    root = tkinter.Tk()
    app = MainWindow(root)

    def test_queue():
        for i in range(10):
            app.queue.put(i)
            time.sleep(1)

    t = threading.Thread(target=test_queue)
    t.start()
    app.mainloop()
    t.join()
    print("finished")

