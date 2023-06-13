import queue
from enum import Enum
from typing import List
import threading
import time


class Priority(Enum):
    low = 0
    medium = 1
    high = 2

    def __lt__(self, other):
        return self.value < other.value

    def __gt__(self, other):
        return self.value > other.value

    def __le__(self, other):
        return self.value <= other.value

    def __ge__(self, other):
        return self.value >= other.value


class Trackable:
    # internal attributes that should not be tracked
    hidden_attributes = ["priority", "linked", "updated", "original", "is_original", "q",
                         "notify_linked", "notify", "update", "clone"]

    dynamic_class_cache = {}

    def __init__(self, obj, original=None):

        original_class = obj.__class__
        if original_class not in self.dynamic_class_cache:
            self.__class__ = self.dynamic_class_cache[original_class] = type(
                f"DynamicClass_{original_class.__name__}",
                (original_class, Trackable), {})
        else:
            self.__class__ = self.dynamic_class_cache[original_class]

        self.__dict__.update(obj.__dict__)
        #print(dir(self))

        self.priority = Priority.low
        self.linked = set()
        self.updated = True
        self.original = original or self
        #print(self.original)
        self.is_original = self is self.original
        self.q = queue.Queue()

        self.obj = obj

    def __setattr__(self, key, value, silent=False):
        if silent or key in Trackable.hidden_attributes or key.startswith("__"):
            super().__setattr__(key, value)
        else:
            self.notify_linked(key, value, self.priority)
            super().__setattr__(key, value)

    def __getattribute__(self, item):
        attr = object.__getattribute__(self, item)
        if hasattr(attr, '__call__') and item not in Trackable.hidden_attributes and not item.startswith("__"):
            def wrapper(*args, **kwargs):
                #print("calling original")
                result = object.__getattribute__(self.original, item)(*args, **kwargs)
                #print("called original")
                return result

            return wrapper
        else:
            return attr

    def clone(self):
        new = Trackable(self.obj, self.original)
        new.linked = self.linked | {self}
        for linked in new.linked:
            linked.linked.add(new)  # todo maybe only keep one reference to linked, in the original trackable
        return new

    def notify_linked(self, key, value, priority):
        # original notifies clones, clones notify original, but clones don't notify other clones
        if self.is_original:
            #print("original notifying clones")
            for linked in self.linked:
                linked.notify(key, value, priority)
        else:
            #print("clone notifying original")
            self.original.notify(key, value, priority)

    def notify(self, key, value, priority):
        self.q.put((key, value, priority))
        self.updated = False
        self.update()

    def update(self):
        while not self.q.empty():
            key, value, priority = self.q.get()
            if priority >= self.priority:
                self.__setattr__(key, value, silent=not self.is_original)  # original should notify clones when updated
        self.updated = True

    def add_attribute(self, name, value):
        self.__setattr__(name, value)


def increment_thread(t: Trackable):
    while True:
        t.value += 1
        time.sleep(0.5)


def print_thread(t: Trackable, t2: Trackable, t3: Trackable):
    while True:
        print(t.value, t2.value, t3.value)
        time.sleep(0.6)


class Example:
    def __init__(self, value):
        self.value = value
        self.x = 1
        self.y = 1
        self.time = time.time()
        print(f"created {self} at {self.time}")

    def increment_x(self):
        self.x += 1

    def increment_y(self):
        self.y += 1

    def increment_value(self):
        self.value += 1

    def print_value(self):
        print(f"{self} value: {self.value}, x: {self.x}, y: {self.y}")

    def __repr__(self):
        return f"Example({self.time})"


def main():
    # thread = threading.Thread(target=increment_thread, args=(t2,))
    # thread.start()
    # thread2 = threading.Thread(target=print_thread, args=(t, t2, t3))
    # thread2.start()

    t = Trackable(Example(0))
    t_clone = t.clone()



if __name__ == '__main__':
    main()
