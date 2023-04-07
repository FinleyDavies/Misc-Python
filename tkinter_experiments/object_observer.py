import tkinter


def notify_method_call(func):
    def wrapper(*args, **kwargs):
        print(f"notifying observers: {func.__name__}(args={args}, kwargs={kwargs})")
        args[0].notify_observers(func.__name__, args[1:] + tuple(kwargs))
        return func(*args, **kwargs)
    return wrapper


class Trackable:
    def __init__(self):
        self._observers = []
        self.test_var = 0

    def __setattr__(self, key, value):
        self.__dict__[key] = value

        if not key.startswith("_"):
            self.notify_observers(key, value)

    def notify_observers(self, key, value):
        print(f"notifying observers: {key} = {value}")
        for observer in self._observers:
            observer.notify(key, value)

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


def main():
    window = tkinter.Tk()

    track = Trackable()
    track.test("hello")


    window.mainloop()

if __name__ == "__main__":
    main()
