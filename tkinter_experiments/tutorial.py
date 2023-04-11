import tkinter as tk
from time import sleep as sl

window = tk.Tk()


def end_program():
    window.destroy()


def get_entry_value():
    name = entry.get()
    print(f"value: {name}")


def reset_entry_value():
    entry.insert(0, "hello")


greeting = tk.Label(text="Hello, World!")
label = tk.Label(
    text="Coloured Label",
    foreground="white",
    background="black",
    height=10,
    width=20
)
button = tk.Button(
    text="EXIT",
    command=end_program
)

button2 = tk.Button(
    text="ENTER",
    command=get_entry_value
)

button3 = tk.Button(
    text="CUSTOM",
    command=reset_entry_value,
    bg="orange",
    fg="blue"
)

entry = tk.Entry()
text_box = tk.Text()


button.pack()
frame1 = tk.Frame()
greeting.pack()
label.pack(anchor="e")
entry.pack(anchor="w")
button2.pack()
button3.pack()
text_box.pack()

# frame1.pack()


window.mainloop()
