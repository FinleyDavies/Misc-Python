import tkinter as tk
from object_observer import Trackable, Mediator, Observer, EVENT_TYPES

import threading


class ObserverApp(tk.Frame):
    """A tkinter app that observes multiple objects and dynamically creates widgets to edit and display their attributes"""

    def __init__(self, observer: Observer, master=None):
        super().__init__()
        self.observer = observer
        self.trackable_properties = observer.get_trackable_attributes()
        self.components = {}

        self.observer.set_notify_callback(self.update_widgets)

        self.pack()

    def update_widgets(self, trackable_name, key, value, type):
        print("updating widgets")
        if type == EVENT_TYPES[0]:
            # create an entry if it doesn't exist
            if key not in self.trackable_properties:
                self.create_entry(trackable_name, key, value)
            else:
                self.components[f"{trackable_name}.{key}"][1].delete(0, tk.END)
                self.components[f"{trackable_name}.{key}"][1].insert(0, value)

            self.trackable_properties[key] = value

    def create_entry(self, trackable_name, key, value):
        label = tk.Label(self, text=f"{trackable_name}.{key}")
        entry = tk.Entry(self)
        entry.insert(0, value)
        self.components[f"{trackable_name}.{key}"] = [label, entry]
        label.pack()
        entry.pack()





def main():
    root = tk.Tk()

    t = Trackable("test")
    m = Mediator()
    app = ObserverApp(Observer(m), master=root)
    m.add_trackable(t)
    t.x = 0

    def input_thread():
        user_input = ""
        while user_input != "quit":
            user_input = input(">>>")
            try:
                t.__setattr__(user_input.split("=")[0], user_input.split("=")[1])
            except Exception as e:
                print(e)


    threading.Thread(target=input_thread).start()
    app.mainloop()




if __name__ == "__main__":
    main()
