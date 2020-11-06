from .ecg import process_ecg
from .gsr import process_gsr
import numpy as np
import sys

class Signal:

    def __init__(self, compute_values, duration_per_compute=120e3, lag_threshold=1e3, should_plot=False):
        self.compute_values = compute_values
        self.duration_per_compute = duration_per_compute
        self.lag_threshold = lag_threshold
        self.should_plot = should_plot
        self.t_points = []
        self.y_points = []

    def add_point(self, t, y):
        if len(self.t_points) > 0:
            # lag = the time between the last point stored and the new point
            last_time_point = self.t_points[-1]
            lag = t - last_time_point

            if lag >= self.lag_threshold:
                # start over using the new time point
                print("too much lag between signals")
                self.clear_points()
        
        # add the new point
        self.t_points.append(t)
        self.y_points.append(y)

        # compute if the signal duration if long enough
        duration = self.get_duration()
        if duration >= self.duration_per_compute:
            t_points_np = np.array(self.t_points)
            y_points_np = np.array(self.y_points)
            res = self.compute_values(t_points_np, y_points_np, self.should_plot)
            self.clear_points()
            return res
        return None

    def clear_points(self):
        self.t_points = []
        self.y_points = []

    def get_duration(self):
        if len(self.t_points) == 0:
            return 0
        start = self.t_points[0]
        end = self.t_points[-1]
        return end - start

def main():
    signal_type = sys.argv[1].lower()
    path_to_samples = sys.argv[2]
    t_points = []
    y_points = []
    with open(path_to_samples, "r") as fin:
        for line in fin:
            a, b = line.rstrip().split(",")
            t_points.append(int(a))
            y_points.append(float(b))
            
    if signal_type == "gsr":
        compute_function = process_gsr
    else:
        compute_function = process_ecg

    signal = Signal(compute_function, should_plot=True, duration_per_compute=120e3)
    for t, y in zip(t_points, y_points):
        res = signal.add_point(t, y)
        if res != None:
            print(res)

if __name__ == "__main__":
    main()