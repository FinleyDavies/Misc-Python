class MyClass:
    def __setattr__(self, key, value):
        print(f"MyClass.__setattr__ {key} {value}")
        super().__setattr__(key, value)

    def __getattribute__(self, key):
        print(f"MyClass.__getattribute__ {key}")
        return super().__getattribute__(key)



my_obj = MyClass()
my_obj.my_attr = 10

my_var = my_obj.my_attr

print(my_var)
my_var = 20
print(my_var)
print(my_obj.my_attr)