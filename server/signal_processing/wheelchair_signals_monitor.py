from .signals import Signal
from .ecg import process_ecg
from .gsr import process_gsr
from .matrix_signal import Matrix_Signal
import numpy as np
import sys

class Wheelchair_Signals_Monitor:
    
    def __init__(self, duration_per_compute=120e3, lag_threshold=1e3, should_plot=False):
        self.ecg_signal = Signal(process_ecg, duration_per_compute, lag_threshold, should_plot)
        self.gsr_signal = Signal(process_gsr, duration_per_compute, lag_threshold, should_plot)
        self.ecg_results = {}
        self.gsr_results = {}
        self.pm_matrix = Matrix_Signal()
        self.wm_matrix = Matrix_Signal()

    def add_point(self, signal_type, t, y):
        ecg_results = None
        gsr_results = None
        if signal_type == "ecg":
            ecg_results = self.ecg_signal.add_point(t, y)
            if ecg_results != None:
                self.ecg_results = ecg_results
        elif signal_type == "gsr":
            gsr_results = self.gsr_signal.add_point(t, y)
            if gsr_results != None:
                self.gsr_results = gsr_results
        elif signal_type == "pm":
            row, column, value = y
            self.pm_matrix.update_cell(row, column, value, t)
        elif signal_type == "wm":
            row, column, value = y
            self.wm_matrix.update_cell(row, column, value, t)
        
        if ecg_results != None or gsr_results != None :
            if len(self.gsr_results) > 0  and len(self.ecg_results) > 0:
                results = {
                    "ecg": self.ecg_results,
                    "gsr": self.gsr_results,
                    "pm": self.pm_matrix.matrix,
                    "wm": self.wm_matrix.matrix
                }
                self.clear()
                return results
        return None

    def clear(self):
        self.ecg_results = {}
        self.gsr_results = {}
        self.ecg_signal.clear_points()
        self.gsr_signal.clear_points()
        self.pm_matrix.clear_matrix()
        self.wm_matrix.clear_matrix()


if __name__ == "__main__":
    x = Wheelchair_Signals_Monitor()

    ecg_t = []
    ecg_y = []
    with open("../ecg.samples", "r") as ecg_in:
        for line in ecg_in:
            t, y = line.rstrip().split(",")
            ecg_t.append(int(t))
            ecg_y.append(float(y))
            
    gsr_t = []
    gsr_y = []
    with open("../gsr.samples", "r") as gsr_in:
        for line in gsr_in:
            t, y = line.rstrip().split(",")
            gsr_t.append(int(t))
            gsr_y.append(float(y))

    for t, y in zip(ecg_t, ecg_y):
        res = x.add_point("ecg", t, y)
        if res != None:
            print(res)

    for t, y in zip(gsr_t, gsr_y):
        res = x.add_point("gsr", t, y)
        if res != None:
            print(res)