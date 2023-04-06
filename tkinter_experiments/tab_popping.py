import tkinter as tk
from tkinter import ttk

root = tk.Tk()

# create a notebook object
notebook = ttk.Notebook(root)

# create tabs
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)

# add tabs to notebook
notebook.add(tab1, text='Tab 1')
notebook.add(tab2, text='Tab 2')

# add some widgets to the tabs
label1 = tk.Label(tab1, text='''This is tab 1
def pop_out_tab():
    notebook.torn(notebook.index('current'))


# create a button to pop out the current tab
pop_out_button = tk.Button(root, text='Pop Out Tab', command=pop_out_tab)
pop_out_button.pack(pady=10)

# display the notebook
notebook.pack()

root.mainloop()''')
label1.pack(padx=10, pady=10)

label2 = tk.Label(tab2, text='''This is tab 2
import tkinter as tk
from tkinter import ttk

root = tk.Tk()

# create a notebook object
notebook = ttk.Notebook(root)

# create tabs
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)

# add tabs to notebook
notebook.add(tab1, text='Tab 1')
notebook.add(tab2, text='Tab 2')''')
label2.pack(padx=10, pady=10)


# create a function to handle popping out the tabs
def pop_out_tab():
    notebook.torn(notebook.index('current'))


# create a button to pop out the current tab
pop_out_button = tk.Button(root, text='Pop Out Tab', command=pop_out_tab)
pop_out_button.pack(pady=10)

# display the notebook
notebook.pack()

root.mainloop()
