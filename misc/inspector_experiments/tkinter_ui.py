import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Tab Widget")
tabControl = ttk.Notebook(root)

# tab1 = ttk.Frame(tabControl)
# tab2 = ttk.Frame(tabControl)
#
# tabControl.add(tab1, text='Tab 1')
# tabControl.add(tab2, text='Tab 2')
# tabControl.pack(expand=1, fill="both")

class AttributeInteraction(ttk.Frame):
    """A class to be used as a base for widgets that allow interaction with a trackable attribute"""
    def __init__(self, trackable, attribute_name):
        super().__init__()

    def lock(self):
        # prevent any other clones of the trackable but this one from changing the original trackable's attribute
        pass



root.mainloop()