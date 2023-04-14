import module_object
import sys
module_object.begin_inspecting()

print(__name__)

a = 10
b = 20
c = 30

print(sys.modules[__name__].__dict__)