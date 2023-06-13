import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style

import time
import threading
import numpy as np

from typing import Dict

from queue_observer import Trackable
from blitmanager import BlitManager


# style.use('fivethirtyeight')

# fig = plt.figure()
# ax1 = fig.add_subplot(1, 1, 1)


class DataObject:
    def __init__(self, start=0):
        self.x = start
        self.y = 0

    def update_thread(self):
        while True:
            # try:
            #     n = int(input("Enter a number:"))
            #     self.x += n
            #     self.y += np.random.randint(-10, 10)
            # except Exception as e:
            #     print(e)
            self.x += np.random.randint(-10, 10)
            self.y = 50 + self.x / 10

            time.sleep(0.05)


def animate(i):
    graph_data = open('../example.txt', 'r').read()
    lines = graph_data.split('\n')
    xs = []
    ys = []
    for line in lines:
        if len(line) > 1:
            x, y = line.split(",")
            xs.append(float(x))
            ys.append(float(y))

    ax1.clear()
    ax1.plot(xs, ys)


class LivePlot:
    def __init__(self, trackable: Trackable, attribute_y, attribute_x=None):
        self.start = time.time()
        self.trackable = trackable
        self._attribute_x = attribute_x
        self._attribute_y = attribute_y

        self._x_values = np.array([])
        self._y_values = np.array([])
        self._times = np.array([])

        # settings:
        self.time_window = 10  # in seconds to show
        self.relative_from_current_time = True  # if true, the x-axis will be relative to the current time

        # todo limit number of datapoints to prevent memory leak

    @property
    def y_values(self):
        return self._y_values

    @property
    def x_values(self):
        if self._attribute_x is None:
            if self.relative_from_current_time:
                return self._times - (time.time() - self.start) + self.time_window

            return self._times
        else:
            return self._x_values

    def update(self):
        self._y_values = np.append(self._y_values, self.trackable.__getattribute__(self._attribute_y))
        if self._attribute_x is not None:
            self._x_values = np.append(self._x_values, self.trackable.__getattribute__(self._attribute_x))
        self._times = np.append(self._times, time.time() - self.start)

    @property
    def values(self):
        return self.x_values, self.y_values


# def live_values(i, live_plot: LivePlot):
#     """live plots the value of a variable"""
#     live_plot.update()
#     ax1.clear()
#     ax1.plot(live_plot.x_values, live_plot.y_values)


class LivePlotter:
    # todo auto scale by creating a new liveplotter object, as rgba buffer needs to be reset with axes new info
    def __init__(self):
        self.time_window = 10  # each plot should inherit this
        self.individual_scale = False  # whether each plot should have its own scale

        self.fig, self.ax = plt.subplots()

        self.blit_manager = BlitManager(self.fig.canvas)

        self.plots: Dict[str, (LivePlot, bool, object)] = {}

    def start(self):
        self.ax.set_xlim(0, self.time_window)
        self.ax.set_ylim(0, 100)
        plt.show(block=False)
        plt.pause(0.01)
        self.plot_thread()

    def plot_thread(self):
        while True:
            self.update()
            plt.pause(0.01)


    def add_plot(self, new_plot: LivePlot, name: str, auto_scale=True):
        ax = self.ax.twinx() if self.individual_scale else self.ax
        (ln,) = ax.plot(*new_plot.values, label=name)
        self.blit_manager.add_artist(ln)

        self.plots[name] = (new_plot, auto_scale, ln)

    def remove_plot(self, name: str):
        # todo test whether removing plot rescales to fit remaining plots
        del self.plots[name]

    def update(self):
        for plot, auto_scale, ln in self.plots.values():
            print(plot.values)
            plot.update()
            ln.set_data(*plot.values)
        self.blit_manager.update()


def main():
    # ani = animation.FuncAnimation(fig, animate, interval=1000)
    # plt.show()

    data = DataObject()
    tracked_data = Trackable(data)
    clone = tracked_data.clone()

    data2 = DataObject(start=-5)
    tracked_data2 = Trackable(data2)
    clone2 = tracked_data2.clone()

    thread = threading.Thread(target=tracked_data.update_thread)
    thread.start()
    thread2 = threading.Thread(target=tracked_data2.update_thread)
    thread2.start()

    live_plot = LivePlot(clone, "y")
    live_plot2 = LivePlot(clone2, "y")

    live_plotter = LivePlotter()
    live_plotter.add_plot(live_plot, "data1")
    live_plotter.add_plot(live_plot2, "data2")
    live_plotter.start()


    # ani = animation.FuncAnimation(fig, live_values, fargs=(live_plot,), interval=100)
    # plt.show()



if __name__ == "__main__":
    main()
