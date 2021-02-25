import matplotlib.pyplot as plt
import sys, os
from signal_processing.gsr import noise_filter
import numpy as np
from signal_processing.ecg import ecg_filter

ROOT_PATH = "./records"

def load_from_file(path):
	x = []
	y = []
	with open(path, "r") as fin:
		for line in fin:
			line = line.rstrip()
			x_element, y_element = line.split(",")
			x.append(x_element)
			y.append(y_element)
	return x, y

def plot(y, label):
	fig, ax = plt.subplots(figsize=(50, 20))
	ax.plot(y)
	ax.set_xlabel("time")
	ax.set_ylabel(label)
	ax.set_title(f"{label} Graph")
	return fig, ax

def main():
	force = False
	if len(sys.argv) > 1:
		if sys.argv[1] == "-f":
			force = True

	for time_id in os.listdir(ROOT_PATH):
		ecg_png_path = f"./{ROOT_PATH}/{time_id}/ecg.png"
		gsr_png_path = f"./{ROOT_PATH}/{time_id}/gsr.png"
		if not force and "ecg.png" in os.listdir(f"{ROOT_PATH}/{time_id}") and "gsr.png" in os.listdir(f"{ROOT_PATH}/{time_id}"):
			print(f"{time_id}: already contains the graph files")
			continue
		ecg_t, ecg = load_from_file(f"{ROOT_PATH}/{time_id}/ecg.txt")
		_, gsr = load_from_file(f"{ROOT_PATH}/{time_id}/gsr.txt")
		gsr = noise_filter(np.array(gsr, dtype=np.float))
		ecg = ecg_filter(np.array(ecg_t, dtype=np.float), np.array(ecg, dtype=np.float))
		ecg_graph = plot(ecg, "ECG")	
		gsr_graph = plot(gsr, "GSR")
		ecg_graph[0].savefig(ecg_png_path)
		gsr_graph[0].savefig(gsr_png_path)
		print(f"{time_id}: graphs saved!")

if __name__ == "__main__":
	main()