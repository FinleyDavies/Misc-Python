import logging
import queue


class Trackable:
    def __init__(self, obj, original=None):
        self.initialised = False

        self.linked = set()
        self.updated = True
        self.original = original or self
        self.is_original = self is self.original
        self.q = queue.Queue()

        self.obj = obj

        self.initialised = True

    def __getattribute__(self, item):
        if item == "__dict__":
            return object.__getattribute__(self, "__dict__")
        items = self.__dict__
        print(items)
        if item in self.__dict__:
            return object.__getattribute__(self, item)


        if hasattr(self.obj, item):
            attr = object.__getattribute__(self.obj, item)
            if hasattr(attr, "__call__"):
                logging.debug(f"{self.obj}.{item}() being called by {self}")
                def wrapper(*args, **kwargs):
                    result = object.__getattribute__(self.obj, item)(*args, **kwargs)
                    return result
                return wrapper

    def __repr__(self):
        return f"Trackable({self.obj}) ({'original' if self.is_original else 'clone'})"

    # def notify(self, key, value, priority, source):
    #     self.q.put((key, value, priority, source))
    #     self.updated = False
    #     self.update()
    #
    # def update(self):
    #     while not self.q.empty():
    #         key, value, priority, source = self.q.get()
    #         if priority >= self.priority:
    #             self.__setattr__(key, value, silent=not self.is_original, source=source)
    #     self.updated = True

    def clone(self):
        new = Trackable(self.obj, self.original)
        new.linked = self.linked | {self}
        for linked in new.linked:
            linked.linked.add(new)
        return new


class Example:
    def __init__(self):
        self.a = 1
        self.b = 2
        self.c = 3
        self.d = 4

    def __repr__(self):
        return f"Example(a={self.a}, b={self.b}, c={self.c}, d={self.d})"

    def increment(self):
        self.a += 1
        self.b += 1
        self.c += 1
        self.d += 1



def main():
    # set up logging:
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)s %(message)s")

    # create an example object:
    example = Example()
    print(example.__dict__)
    trackable = Trackable(example)
    clone = trackable.clone()
    clone.increment()
    print(example)



if __name__ == "__main__":
    main()
