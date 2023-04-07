import tkinter


def notify_method_call(func):
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        args[0].notify_observers(func.__name__, args[1:])
        return func(*args, **kwargs)


class Trackable:
    def __init__(self):
        self.observers = []

    def __setattr__(self, key, value):
        for observer in self.observers:
            observer.notify(key, value)

    def notify_observers(self, key, value):
        for observer in self.observers:
            observer.notify(key, value)

    @notify_method_call
    def add_observer(self, observer):
        self.observers.append(observer)

    @notify_method_call
    def remove_observer(self, observer):
        self.observers.remove(observer)


def main():
    window = tkinter.Tk()

    track = Trackable()


    window.mainloop()

if __name__ == "__main__":
    main()
