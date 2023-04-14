import inspect
from types import FunctionType, MethodType
import textwrap


class Original:
    """Original class to be modified"""

    def __init__(self, numbers):
        self.numbers = numbers
        self.a = 1
        self.b = 2
        self.c = 3

    def do_thing(self):
        print("original object method: do_thing")
        print(self.a)
        print(self.b)

    def do_other_thing(self):
        print(f"original object method: do_other_thing")
        print(f"a + b = {self.a + self.b}")

    def increment_a(self):
        self.a += 1


class Modified:
    def __init__(self, original):
        class DynamicClass(original.__class__, Modified):
            pass

        print(original.__dict__)
        self.__class__ = DynamicClass

        self.__dict__ = original.__dict__

    @staticmethod
    def notify_method_call(func):
        def wrapper(self, *args, silent=False, **kwargs):
            name = func.__name__
            if not silent:
                print(f"method {name} called with args={args}, kwargs={kwargs}")
            return func(self, *args, **kwargs)

        return wrapper



def main():

    obj1 = Original([1, 2, 3])
    string = "hello"



    modded = Modified(obj1)
    modded_string = Modified(string)

    modded.do_thing()
    modded.do_other_thing()
    modded.increment_a()

    print(f"modded.a: {modded.a}")
    modded.a = 10

    modded.__setattr__("a", 20)


if __name__ == "__main__":
    main()
