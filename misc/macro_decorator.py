import inspect
import textwrap


class Trackable:
    def __init__(self, name):
        self.name = name

    def __setattr__(self, key, value):
        print(f"Trackable.__setattr__ {key} {value}")
        super().__setattr__(key, value)

    def add_vars(self, *vars):
        for var in vars:
            self.__setattr__(var, None)


global_tracker = Trackable("global_tracker")


def track_vars_custom(trackable: Trackable, *to_track):
    """Decorator to track variables in a function.
    adds the variables to the trackable object and macros the function to refer to the trackable object."""

    def decorator(func):
        trackable.add_vars(*to_track)

        source = inspect.getsourcelines(func)[0][1:]
        source = textwrap.dedent("".join(source))

        for var in to_track:
            if var not in source:
                raise ValueError(f"Variable {var} not found in function {func.__name__}")
            else:
                source = source.replace(var, f"{trackable.name}.{var}")

        wrapper = compile(source, func.__name__, "exec")
        namespace = {}
        exec(wrapper, globals(), namespace)

        return namespace[func.__name__]

    return decorator


def track_vars(*to_track):
    return track_vars_custom(global_tracker, *to_track)


def main():
    @track_vars("my_var", "foo")
    def test():
        my_var = 10
        foo = "hello"
        foo += " world"
        my_var = len(foo)
        print(my_var)

    test()


if __name__ == "__main__":
    main()
