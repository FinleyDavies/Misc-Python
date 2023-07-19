import queue
from enum import Enum
from typing import List
import threading
import time

import logging

from typing import Dict, Set


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
                         "notify_linked", "notify", "update", "clone", "attribute_edit", "dynamic_class_cache"]

    dynamic_class_cache = {}
    attribute_edit: Dict[str, Set[object]] = {}  # set of trackables that can edit each attribute

    # should only be used by the original trackable, not clones

    def __init__(self, obj, original=None):

        original_class = obj.__class__
        if original_class not in self.dynamic_class_cache:
            self.__class__ = self.dynamic_class_cache[original_class] = type(
                f"DynamicClass_{original_class.__name__}",
                (original_class, Trackable), {})
        else:
            self.__class__ = self.dynamic_class_cache[original_class]

        self.__dict__.update(obj.__dict__)

        self.priority = Priority.low
        self.linked = set()
        self.updated = True
        self.original = original or self
        self.is_original = self is self.original
        self.q = queue.Queue()

        self.obj = obj



    def __setattr__(self, key, value, silent=False, source=None):
        source = source or self
        allowed_trackables = self.attribute_edit.get(key, set())

        if allowed_trackables and source not in allowed_trackables:  # empty set means all trackables can edit
            logging.debug(f"{self}.{key} is not allowed to be edited by {source}")
            return

        # if the source of the attribute change is not allowed to edit the attribute, ignore the change

        super().__setattr__(key, value)

        if silent or key in Trackable.hidden_attributes or key.startswith("__"):
            return

        self.notify_linked(key, value, self.priority)

    def __getattribute__(self, item):
        attr = object.__getattribute__(self, item)
        if hasattr(attr, '__call__') and item not in Trackable.hidden_attributes and not item.startswith("__"):

            def wrapper(*args, **kwargs):
                logging.debug(f"calling {item} in {self}")
                result = object.__getattribute__(self.original, item)(*args, **kwargs)
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
            for linked in self.linked:
                linked.notify(key, value, priority, source=self)
        else:
            self.original.notify(key, value, priority, source=self)

    def notify(self, key, value, priority, source)\
            :
        self.q.put((key, value, priority, source))
        self.updated = False
        self.update()

    def update(self):
        while not self.q.empty():
            key, value, priority, source = self.q.get()
            if priority >= self.priority:
                self.__setattr__(key, value, silent=not self.is_original, source=source)
        self.updated = True

    def add_attribute(self, name, value):
        self.__setattr__(name, value)

    def __repr__(self):
        print("calling repr on trackable")
        return self.obj.__repr__() + " (trackable)"

def increment_thread(t: Trackable):
    while True:
        t.value += 1
        time.sleep(0.5)


def print_thread(t: Trackable, t2: Trackable, t3: Trackable):
    while True:
        print(t.value, t2.value, t3.value)
        time.sleep(0.6)


class Example:
    def __init__(self, value, name):
        self.name = name
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
        print(f"{self} value: {self.value}, x: {self.x}, y: {self.y}\n")

    def __repr__(self):
        print("calling repr on example")
        return f"Example({self.name})"


def main():
    # thread = threading.Thread(target=increment_thread, args=(t2,))
    # thread.start()
    # thread2 = threading.Thread(target=print_thread, args=(t, t2, t3))
    # thread2.start()

    t = Trackable(Example(0, "t"))
    t_clone = t.clone()
    print(dir(t_clone))
    print(t_clone.__repr__())


if __name__ == '__main__':
    main()
