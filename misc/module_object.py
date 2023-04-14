import sys
import inspect
from types import ModuleType


class TrackableModule(ModuleType):
    def __init__(self, module):
        super().__init__(module.__name__)
        # self.__class__ = type(module.__name__, (self.__class__, module.__class__), {})
        self.__dict__.update(module.__dict__)
        self.test = 10

    def __setattr__(self, key, value):
        print(f"TrackableModule.__setattr__ {key} {value}")
        super().__setattr__(key, value)


def begin_inspecting():
    mod = sys.modules["__main__"]
    del sys.modules["__main__"]
    sys.modules["__main__"] = TrackableModule(mod)

