import sys
import types

def original_print(*args, **kwargs):
    print("original print")
    print(*args, **kwargs)

def patched_print(*args, **kwargs):
    print("patched print")
    print(original_print.__code__)

original_print = patched_print

original_print("hello")

def cursed_decorator(func):
    try:
        print(f"adding {func.__name__} to globals")
        print(f"wrapper thing: {func.thing}")
        sys.modules[__name__].__dict__[func.__name__] = eval("print(func.__name__)")

        def cursed_decorator_2(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        return cursed_decorator_2
    except:
        pass

#sys.modules[__name__].__dict__["hello"] = eval("hello(x)\nprint('hello')")

d = "hello"
@cursed_decorator
def hello(x):
    print("hello")
    print(x)
    yield x

def a(x):
    print("a")
    print(x:=x+1)
    return x

def b(x):
    print("b")
    print(x := x + 1)
    return x

def c(x):
    print("c")
    print(x := x + 1)
    return x

def d(x):
    print("d")
    print(x := x + 1)
    return x

def a2(x):
    print("a2")

    yield next(x)

def b2(x):
    print("b2")

    yield next(x)

def c2(x):
    print("c2")

    yield next(x)

def d2(x):
    print("d2")

    yield next(x)

# a(b(c(d(1))))
# next(a2(b2(c2(d2(iter([1]))))))
print("hello")