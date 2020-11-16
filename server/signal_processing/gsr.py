from scipy.signal import lfilter, find_peaks
import matplotlib.pyplot as plt
import numpy as np

def noise_filter(signal):
    n = 10
    b = [1.0 / n] * n
    a = 1
    return lfilter(b, a, signal)

def compute_values():
    y = np.array(self.y_points)
    t = np.array(self.t_points)
    y = self.noise_filter(y)
    return (t, y)

def process_gsr(t_points, y_points, should_plot=False):
    y = noise_filter(y_points)
   
    if should_plot:
        fig, ax = plt.subplots()
        ax.plot(y)
        plt.show()

    return {
        "max": np.max(y),
        "min": np.min(y),
        "mean": np.mean(y),
        "median": np.median(y),
        "std": np.std(y),
        "variance": np.var(y)
    }