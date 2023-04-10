import tkinter

from queue import Queue




class Threshold:
    def __init__(self):
        pass



class Trackable:
    def __init__(self, name):
        self._observers = []
        self.test_var = 0
        self.name = name

        self.input_queue = Queue()
        self.output_queue = Queue()

    def __setattr__(self, key, value, silent=False):
        self.__dict__[key] = value

        if key.endswith("_threshold"):
            return
        if key.startswith("_"):
            return

        threshold = self.__dict__.get(f"{key}_threshold", None)
        if threshold is not None:
            pass

        if not silent:
            print("setting attribute")
            self.notify_observers(key, value)





    def notify_observers(self, key, value):
        print(f"notifying observers: {key} = {value}")
        for observer in self._observers:
            observer.notify(self.name, key, value)

    @staticmethod
    def notify_method_call(func):
        def wrapper(*args, **kwargs):
            print("function called")
            print(f"notifying observers: {func.__name__}(args={args}, kwargs={kwargs})")
            args[0].notify_observers(func.__name__, args[1:] + tuple(kwargs))
            return func(*args, **kwargs)

        return wrapper

    @notify_method_call
    def add_observer(self, observer):
        self._observers.append(observer)

    @notify_method_call
    def remove_observer(self, observer):
        self._observers.remove(observer)

    @notify_method_call
    def test(self, arg):
        self.test_var = arg
        print(f"test: {arg}")


class Observer:
    def __init__(self, trackable: Trackable):
        self.queue = Queue()
        self.trackable = trackable
        self.trackable.add_observer(self)


    def notify(self, trackable, key, value):
        print(f"observer notified: {trackable} {key} = {value}")


class Editor:
    def __init__(self, trackable: Trackable):
        self.trackable = trackable
        self.trackable.add_observer(self)

def main():
    window = tkinter.Tk()

    track = Trackable("test")
    track.test("hello")


    window.mainloop()

if __name__ == "__main__":
    main()
