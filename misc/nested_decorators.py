def decorator1(func):
    def wrapper(*args, **kwargs):
        print("decorator1 start")
        value = func(*args, **kwargs)
        print(f"decorator1: {value}")
        print("decorator1 end")
        return value
    return wrapper

def decorator2(func):
    def wrapper(*args, **kwargs):
        print("decorator2 start")
        value = func(*args, **kwargs)
        print(f"decorator2: {value}")
        print("decorator2 end")
        return value
    return wrapper

def decorator3(func):
    def wrapper(*args, **kwargs):
        print("decorator3 start")
        value = func(*args, **kwargs)
        print(f"decorator3: {value}")
        print("decorator3 end")
        return value
    return wrapper

@decorator1(decorator2(decorator3))
def test():
    return "test"

@decorator1
@decorator2
@decorator3
def test2():
    return "test2"

test()
print("")
test2()

