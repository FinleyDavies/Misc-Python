from __future__ import annotations
import tkinter
import time

from typing import Dict, List, Callable
import threading
import re
import logging

EVENT_TYPES = ["set_attribute", "method_call", "within_threshold", "trackable_added", "trackable_removed"]


class Trackable:
    def __init__(self, name):
        self._mediators = []
        self._lock = threading.Lock()

        self._trackable_attributes = {}
        self._trackable_methods = {}

        self.name = name
        self.test(5)

    def __setattr__(self, key, value, silent=False):
        if key.startswith("_"):
            super().__setattr__(key, value)
            return

        self._trackable_attributes[key] = value

        if not silent:
            print(f"{self.__class__.__name__}({self.name}) setting {key} = {value}")
            self.notify_mediators(key, value, EVENT_TYPES[0])

    def __getattr__(self, item):
        if item.startswith("_"):
            return self.__dict__[item]
        else:
            return self._trackable_attributes[item]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name})"

    def get_lock(self):
        return self._lock

    def add_mediator(self, mediator):
        self._mediators.append(mediator)

        mediator.notify(self.name, self.name, [self.get_trackable_attributes(), self.get_trackable_methods()],
                        EVENT_TYPES[3])

    def remove_mediator(self, mediator):
        self._mediators.remove(mediator)

    def notify_mediators(self, key, value, type):
        for mediator in self._mediators:
            print(f"notifying {mediator} of {self.name}.{key} = {value}")
            mediator.notify(self.name, key, value, type)

    def get_trackable_attributes(self):
        return self._trackable_attributes

    def get_trackable_methods(self):
        return self._trackable_methods

    def invoke(self, method_name, *args, **kwargs):
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            method2 = method
            return method(*args, **kwargs)
        else:
            raise AttributeError(f"{self} has no attribute {method_name}")

    @staticmethod
    def notify_method_call(func):

        def wrapper(self, *args, silent=False, **kwargs):
            name = func.__name__
            if name not in self._trackable_methods:
                self._trackable_methods[name] = 0
            self._trackable_methods[name] += 1

            print("function called")
            print(f"notifying mediators: {name}(args={args}, kwargs={kwargs})")

            if not silent:
                self.notify_mediators(name, args + tuple(kwargs), EVENT_TYPES[1])

            return func(self, *args, **kwargs)

        return wrapper

    @notify_method_call
    def test(self, depth):
        print(f"test called with depth {depth}")
        if depth > 0:
            self.test(depth - 1)


class Mediator:
    def __init__(self, trackables: List[Trackable] = None, observers: List[Observer] = None):
        self._trackables: Dict[str, Trackable] = {}
        self._observers: List[Observer] = []
        self._lock = threading.RLock()

    def __repr__(self):
        return f"{self.__class__.__name__}({len(self._trackables)} trackables, {len(self._observers)} observers)"

    def add_trackable(self, trackable: Trackable):
        with self._lock and trackable.get_lock():
            new_name = trackable.name
            while new_name in self._trackables:
                if re.search(r"(\d+)$", new_name):
                    new_name = re.sub(r"(\d+)$", lambda m: str(int(m.group(1)) + 1), new_name)
                else:
                    new_name += "2"

            trackable.name = new_name

            self._trackables[new_name] = trackable
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

    def set_attribute(self, trackable_name, key, value):
        """Set an attribute on a trackable and notify observers."""
        trackable = self._trackables[trackable_name]
        with self._lock:
            trackable.__setattr__(key, value)

    def invoke_method(self, trackable_name, method_name, args=None, kwargs=None):
        """Invoke a method on a trackable and notify observers."""
        args = args or []
        kwargs = kwargs or {}
        trackable = self._trackables[trackable_name]
        with trackable.get_lock():
            print(f"invoking {trackable_name}.{method_name}({args}, {kwargs})")
            trackable.invoke(method_name, *args, **kwargs)

    def get_all_attributes(self):
        """Get all attributes of all trackables."""
        with self._lock:
            return {trackable_name: trackable.get_trackable_attributes() for trackable_name, trackable in
                    self._trackables.items()}

    def get_all_methods(self):
        """Get all methods of all trackables."""
        with self._lock:
            return {trackable_name: trackable.get_trackable_methods() for trackable_name, trackable in
                    self._trackables.items()}


class Observer:
    def __init__(self, mediator: Mediator, notify_callback: Callable = None):
        self.mediator = mediator
        self.mediator.add_observer(self)
        self.notify_callback = notify_callback

    def set_notify_callback(self, callback):
        self.notify_callback = callback

    def notify(self, trackable_name, key, value, type):
        print(f"observer: {trackable_name}.{key} = {value} ({type})")
        if self.notify_callback:
            self.notify_callback(trackable_name, key, value, type)

    def set_attribute(self, trackable_name, key, value):
        self.mediator.set_attribute(trackable_name, key, value)

    def invoke_method(self, trackable_name, method_name, args=None, kwargs=None):
        self.mediator.invoke_method(trackable_name, method_name, args, kwargs)

    def get_trackable_attributes(self, trackable_name=None):
        if trackable_name is None:
            return self.mediator.get_all_attributes()
        return self.mediator.get_all_attributes()[trackable_name]


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
    track2.x = 1

    mediator.set_attribute("test", "x", 2)
    mediator.invoke_method("test", "__setattr__", args=("x", 3))

    window.mainloop()


if __name__ == "__main__":
    main()
