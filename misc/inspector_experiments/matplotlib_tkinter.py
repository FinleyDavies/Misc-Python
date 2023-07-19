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


class LivePlot:
    def __init__(self, trackable: Trackable, name: str, attribute_y, attribute_x=None, time_window=10):
        self.start = time.time()
        self.trackable = trackable
        self.name = name
        self._attribute_x = attribute_x
        self._attribute_y = attribute_y

        self._x_values = np.array([])
        self._y_values = np.array([])
        self._times = np.array([])
        self.update()

        # settings:
        self.time_window = 10  # in seconds to show
        self.relative_from_current_time = True  # if true, the x-axis will be relative to the current time
        # with past values being negative, if false, time will be absolute

        # todo limit number of datapoints to prevent memory leak

    @property
    def x_values(self):
        if self._attribute_x is None:
            if self.relative_from_current_time:
                return self._times - self._times[-1]
            else:
                return self._times
        else:
            return self._x_values

    def get_data(self, offset=0):
        # mask out any values older than time_window:
        mask = self._times > self._times[-1] - self.time_window
        return self.x_values[mask] + offset, self._y_values[mask]

    def update(self):
        self._y_values = np.append(self._y_values, self.trackable.__getattribute__(self._attribute_y))
        if self._attribute_x is not None:
            self._x_values = np.append(self._x_values, self.trackable.__getattribute__(self._attribute_x))
        self._times = np.append(self._times, time.time() - self.start)

    def set_time_window(self, time_window):
        self.time_window = time_window

    def is_truncated(self):
        return self._times[0] < self._times[-1] - self.time_window


class LivePlotter:
    def __init__(self):
        self.time_window = 5  # each plot should inherit this
        self.max_time_window = 30  # maximum time window to show
        self.individual_scale = False  # whether each plot should have its own scale

        self.fig, self.ax = plt.subplots()

        self.blit_manager = BlitManager(self.fig.canvas)

        self.plots: Dict[str, (LivePlot, object)] = {}

        #todo add optional labels to lines
        #todo autoscale y axis

    def start(self):
        self.ax.set_xlim(0, self.time_window)
        self.ax.set_ylim(0, 100)
        plt.show(block=False)
        plt.pause(0.01)
        self.plot_thread()

    def plot_thread(self):
        start = time.time()
        x = 2
        while True:
            self.update()
            plt.pause(0.01)
            if self.time_window < self.max_time_window and self.is_truncated():
                self.update_time_window(self.time_window * 2)

    def add_plot(self, new_plot: LivePlot):
        new_plot.set_time_window(self.time_window)
        ax = self.ax.twinx() if self.individual_scale else self.ax
        (ln,) = ax.plot(*new_plot.get_data(self.time_window), label=new_plot.name)
        self.blit_manager.add_artist(ln)

        self.plots[new_plot.name] = (new_plot, ln)

    def offset_by_time(self, values, time_offset):
        return values[0] + time_offset, values[1]

    def remove_plot(self, name: str):
        # todo test whether removing plot rescales to fit remaining plots
        del self.plots[name]

    def update(self):
        for plot, ln in self.plots.values():
            plot.update()
            ln.set_data(*plot.get_data(self.time_window))
        self.blit_manager.update()

    def update_time_window(self, time_window):
        self.time_window = time_window if time_window < self.max_time_window else self.max_time_window
        for plot, ln in self.plots.values():
            plot.set_time_window(self.time_window)
            ln.set_data(*plot.get_data(self.time_window))
        # update plot axes:
        self.ax.set_xlim(0, self.time_window)
        self.blit_manager.update()

    def is_truncated(self):
        return any(plot.is_truncated() for plot, ln in self.plots.values())


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

    live_plot = LivePlot(clone, "plot1", "y")
    live_plot2 = LivePlot(clone2, "plot2", "y")

    live_plotter = LivePlotter()
    live_plotter.add_plot(live_plot)
    live_plotter.add_plot(live_plot2)
    live_plotter.start()

    # ani = animation.FuncAnimation(fig, live_values, fargs=(live_plot,), interval=100)
    # plt.show()


if __name__ == "__main__":
    main()
