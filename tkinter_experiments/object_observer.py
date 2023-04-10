from __future__ import annotations
import tkinter
import time


from queue import Queue
from typing import Dict, List
import threading
import re

EVENT_TYPES = ["set_attribute", "method_call", "within_threshold"]

def debug_decorator(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        print(f"calling {func.__name__} with args={args}, kwargs={kwargs}")
        value = func(*args, **kwargs)
        print(f"called {func.__name__}, took {time.time() - start_time} seconds")

        return value

    return wrapper

class Trackable:
    def __init__(self, name):
        self._mediators = []
        self._lock = threading.Lock()

        self.name = name

    def __setattr__(self, key, value, silent=False):
        self.__dict__[key] = value

        if key.startswith("_"):
            return

        if not silent:
            self.notify_mediators(key, value, EVENT_TYPES[0])

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def get_lock(self):
        return self._lock

    def add_mediator(self, mediator):
        self._mediators.append(mediator)

    def remove_mediator(self, mediator):
        self._mediators.remove(mediator)

    def notify_mediators(self, key, value, type):
        for mediator in self._mediators:
            mediator.notify(self.name, key, value, type)

    def get_args(self):
        return self.__dict__.items()

    def invoke(self, method_name, *args, **kwargs):
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            method2 = method
            print(method == self.__setattr__)
            return method(*args, **kwargs)
        else:
            raise AttributeError(f"{self} has no attribute {method_name}")

    @staticmethod
    def notify_method_call(func):
        def wrapper(*args, silent=False, **kwargs):
            print("function called")
            print(f"notifying mediators: {func.__name__}(args={args}, kwargs={kwargs})")
            if not silent:
                args[0].notify_mediators(func.__name__, args[1:] + tuple(kwargs), EVENT_TYPES[1])
            return func(*args, **kwargs)

        return wrapper


class Mediator:
    def __init__(self, trackables: List[Trackable] = None, observers: List[Observer] = None):
        self._trackables: Dict[str, Trackable] = {}
        self._observers: List[Observer] = []
        self._lock = threading.Lock()

    def add_trackable(self, trackable: Trackable):
        with self._lock and trackable.get_lock():
            new_name = trackable.name
            while new_name in self._trackables:
                if re.search(r"(\d+)$", new_name):
                    new_name = re.sub(r"(\d+)$", lambda m: str(int(m.group(1)) + 1), new_name)
                else:
                    new_name += "2"

            trackable.__setattr__("name", new_name, silent=True)


            self._trackables[trackable.name] = trackable
            trackable.add_mediator(self)

    def remove_trackable(self, trackable: Trackable):
        with self._lock:
            self._trackables.pop(trackable.name)
            trackable.remove_mediator(self)

    def add_observer(self, observer):
        with self._lock:
            self._observers.append(observer)

    def remove_observer(self, observer):
        with self._lock:
            self._observers.remove(observer)

    def notify(self, trackable_name, key, value, type):
        """Notify observers of a change to a trackable."""
        with self._lock:
            for observer in self._observers:
                observer.notify(trackable_name, key, value, type)

    @debug_decorator
    def set_attribute(self, trackable_name, key, value):
        """Set an attribute on a trackable and notify observers."""

        with self._trackables[trackable_name]._lock:
            self._trackables[trackable_name].__setattr__(key, value)

    @debug_decorator
    def invoke_method(self, trackable_name, method_name, args=None, kwargs=None):
        """Invoke a method on a trackable and notify observers."""
        args = args or []
        kwargs = kwargs or {}
        with self._trackables[trackable_name]._lock:
            print(f"invoking {trackable_name}.{method_name}({args}, {kwargs})")
            self._trackables[trackable_name].invoke(method_name, *args, **kwargs)


class Observer:
    def __init__(self, mediator: Mediator):
        self.mediator = mediator
        self.mediator.add_observer(self)

    def notify(self, trackable_name, key, value, type):
        print(f"observer: {trackable_name}.{key} = {value}")

    def set_attribute(self, trackable_name, key, value):
        self.mediator.set_attribute(trackable_name, key, value)

    def invoke_method(self, trackable_name, method_name, args=None, kwargs=None):
        self.mediator.invoke_method(trackable_name, method_name, args, kwargs)


def main():
    window = tkinter.Tk()

    track = Trackable("test")
    track2 = Trackable("test")
    track3 = Trackable("test")
    mediator = Mediator()
    observer = Observer(mediator)
    observer2 = Observer(mediator)

    mediator.add_trackable(track)
    mediator.add_trackable(track2)
    mediator.add_trackable(track3)

    track.x = 0
    track.x += 1

    mediator.set_attribute("test", "x", 2)
    mediator.invoke_method("test", "__setattr__", args=("x", 3))


    window.mainloop()


if __name__ == "__main__":
    main()
