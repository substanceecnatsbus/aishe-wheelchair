from .signals import Signal
from .ecg import process_ecg
from .gsr import process_gsr
from .matrix_signal import Matrix_Signal
import time, os

class Wheelchair_Signals_Monitor:
    
    def __init__(self, duration_per_compute=120e3, lag_threshold=2e3, should_record=True, pressure_threshold=0):
        self.duration_per_compute = duration_per_compute
        self.lag_threshold = lag_threshold
        self.signals = {}
        self.signals["ecg"] = Signal(process_ecg)
        self.signals["gsr"] = Signal(process_gsr)
        self.signals["pm"] = Matrix_Signal("Pressure Matrix", threshold=pressure_threshold)
        self.signals["wm"] = Matrix_Signal("Wetness Matrix")
        self.should_record = should_record
        self.features = {}

    def add_point(self, signal_type, t, y):
        if signal_type == "ecg" or signal_type == "gsr":
            self.signals[signal_type].add_point(t, y)
            # start over if lag is over lag threshold
            lag = self.signals[signal_type].get_lag()
            if lag >= self.lag_threshold:
                print(f"too much lag between {signal_type} signals")
                self.clear()
        else:
            row, column, value = y
            matrix_res = self.signals[signal_type].update_cell(row, column, value, t)
            if matrix_res == 1:
                # user detected
                return 3
            elif matrix_res == 2:
                # no user detected
                self.clear()
                return 2
        
        # extract features when signal duration is enough
        ecg_duration = self.signals["ecg"].get_duration()
        if ecg_duration >= self.duration_per_compute:
            self.compute_features()
            # do inference/data gathering
            return 1
        # do nothing
        return 0

    def compute_features(self):
        time_id = time.time()
        results = {
            "time_id": time_id,
            "ecg": self.signals["ecg"].extract_features(),
            "gsr": self.signals["gsr"].extract_features(),
            "pm": self.signals["pm"].matrix,
            "wm": self.signals["wm"].matrix
        }
        self.record(time_id)
        self.clear()
        self.features = results
        return results

    def clear(self):
        self.signals["ecg"].clear_points()
        self.signals["gsr"].clear_points()
        self.signals["pm"].clear_matrix()
        self.signals["wm"].clear_matrix()

    def record(self, time_id):
        dir_path = f"./records/{time_id}"
        os.mkdir(dir_path)
        with open(f"{dir_path}/ecg.txt", "w") as fout:
            for t, y in zip(self.signals["ecg"].t_points, self.signals["ecg"].y_points):
                fout.write(f"{t},{y}\n")
        with open(f"{dir_path}/gsr.txt", "w") as fout:
            for t, y in zip(self.signals["gsr"].t_points, self.signals["gsr"].y_points):
                fout.write(f"{t},{y}\n")
        print(f"{time_id}: signals recorded")

if __name__ == "__main__":
    # :DD
    x = Wheelchair_Signals_Monitor(duration_per_compute=120e3, lag_threshold=1e3, should_record=False)
    with open("./gsr.samples", "r") as fin_gsr:
        for line_gsr in fin_gsr:
            line_gsr = line_gsr.rstrip()
            t, y = list(map(float, line_gsr.split(",")))
            x.add_point("gsr", t, y)
    with open("./ecg.samples", "r") as fin_ecg:
        for line_ecg in fin_ecg:
            line_ecg = line_ecg.rstrip()
            t, y = list(map(int, line_ecg.split(",")))
            z = x.add_point("ecg", t, y)
            if z != None:
                print(z)