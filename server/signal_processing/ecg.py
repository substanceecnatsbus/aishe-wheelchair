import matplotlib.pyplot as plt

####
# system imports
import os
import sys
import math
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
from scipy.interpolate import interp1d
from scipy import stats
import heartpy as hp
from numpyencoder import NumpyEncoder
import datetime

####################################

def interpolateRawSignal(rawTimes, rawValues, rawRows, rawDuration):
    duration = np.round(rawDuration)
    interpMultiplier = duration * 100
    rows = int(math.ceil(rawRows / interpMultiplier) * interpMultiplier)
    fs = rows // duration
    interpolator = interp1d(rawTimes, rawValues)
    ecgTimes = np.linspace(rawTimes[0], rawTimes[-1], num=rows)
    ecgValues = interpolator(ecgTimes)

    # convert nans to number next to it
    for i in range(len(ecgValues) - 1):
        if np.isnan(ecgValues[i]):
            ecgValues[i] = ecgValues[i + 1]

    # print(f"#Interpolated | rows: {rows}, duration: {duration}, fs: {fs}")

    return ecgTimes, ecgValues, rows, duration, fs

# 3rd order butterworth lowpass filter, 20 hz cutoff frequency
def butter_lowpass(cutoff, sample_freq, order=5):
    nyq = 0.5 * sample_freq     # nyquist frequeny is half the sampling frequency
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = signal.lfilter(b, a, data)
    return y

def filterEcgSignal(ecgValues, fs):
    # 5th order lowpass butterworth filter, 15 Hz cutoff frequency
    cutoffFrequency, filterOrder = 15, 5        # TODO: change values if bad filter
    filteredValues = butter_lowpass_filter(ecgValues, cutoffFrequency, fs, filterOrder)

    # to remove very low values cause by filtering the signal
    minThreshold = np.min(np.mean(filteredValues)) * 0.80  # 80% of mean value
    filteredValues = np.array([x if x >= minThreshold else minThreshold for x in filteredValues])

    return filteredValues

def findPeaks(filteredValues, fs):
    windowData, measure = hp.process(filteredValues, sample_rate=fs, calc_freq=True)
    peaks = windowData['peaklist']

    # remove very close peaks - probably false peak detected
    peakFindingIteration = 3    # TODO: change values if there are VERY CLOSE fake peaks detected
    for q in range(peakFindingIteration):
        peaksToRemove = []
        # TODO: change value if threshold too high or too low
        peakWidthThreshold = np.mean(np.diff(peaks)) * 0.60     # 60% of average peak widths
        # print(f"peak finding iteration {q}: threshold: {peakWidthThreshold}, aveWidth: {np.mean(np.diff(peaks))}")

        for i in range(len(peaks) - 1):
            cur, nxt = peaks[i], peaks[i + 1]
            if(abs(nxt - cur) < peakWidthThreshold):
                peaksToRemove.append(cur if filteredValues[cur] < filteredValues[nxt] else nxt)

        peaks = [x for x in peaks if x not in peaksToRemove]

    return peaks

def getParameters(peakTimes, peaks, rows, fs):
    # use this to determine where the wrong peaks are
    # print("Determine peak diffs - if right value is a lot greater than average, probably needs a peak in there")
    # print("Average", np.average(np.diff(peakTimes)))
    # for i, pt in enumerate(np.diff(peakTimes)):
    #     print(f"{i+1} - {pt}")

    # Time Domain Analysis
    RR_list = np.diff(peakTimes)            # list of RR Intervals
    RR_diff = np.abs(np.diff(RR_list))      # difference between RR Intervals
    RR_sqdiff = RR_diff ** 2                # squared difference between RR Intervals

    RR_mean = np.round(np.mean(RR_list), 4)              # (Mean RRI) ==> mean of RR Intervals
    RR_std = np.round(np.std(RR_list), 4)                # (SDRR) ==> standard deviation of RR Intervals
    RR_cv = np.round(stats.variation(RR_list) * 100, 4)  # (CVRR) ==> coefficient of variation (CV) or RR Intervals in %
    RR_sdsd = np.round(np.std(RR_diff), 4)               # (SDSD) ==> standard deviation of difference between RR Intervals
    heartRate = np.round(60e3 / RR_mean, 4)              # average heart rate

    # Frequency Domain Analysis
    RR_x = peaks[1:]            # remove first entry, 1st interval is assigned to 2nd beat
    RR_y = np.diff(peakTimes)              # Y-values are equal to interval lengths
    RR_x_new = np.linspace(RR_x[0], RR_x[-1], RR_x[-1])     # create evenly space timeline
    RR_interpolator = interp1d(RR_x, RR_y, kind='cubic')    # interpolate signal with cubic spline interpolation
    RR_y_new = RR_interpolator(RR_x_new)                    # new values of interpolated signal

    # Find the frequencies that make up the interpolated signal
    n = rows
    side = range(int(n / 2))
    frq = np.fft.fftfreq(n, d=(1 / fs))     # divide the bits into frequency categories
    frq = frq[side]                         # get single side of the frequency range

    # Do FFT
    Y = np.fft.fft(RR_y_new) / n    # calculate FFT
    Y = Y[side]                     # return 1 side of the FFT

    # Calculate LH Ratio
    lf = np.trapz(abs(Y[(frq >= 0.04) & (frq <= 0.15)]))
    hf = np.trapz(abs(Y[(frq >= 0.16) & (frq <= 0.5)]))
    LH_ratio = np.round(lf / hf, 4)

    # Emotion Analysis
    emotion = None

    if RR_cv > 6.5 and RR_cv <= 10:
        if LH_ratio > 1:
            emotion = "Angry"
        elif (LH_ratio >= 0.65 and LH_ratio <= 1):
            emotion = "Fear"
        elif LH_ratio < 0.65:
            emotion = "Peace"
    elif (RR_cv >= 5.5 and RR_cv <= 6.5):
        emotion = "Peace"
    elif RR_cv < 5.5:
        if LH_ratio > 1:
            emotion = "Happy"
        elif (LH_ratio >= 0.65 and LH_ratio <= 1):
            emotion = "Sad"
        elif LH_ratio < 0.65:
            emotion = "Peace"
    else:
        emotion = "Unknown"

    result = {
        "Mean RRI": np.round(RR_mean, 4),
        "CVRR": np.round(RR_cv, 4),
        "SDRR": np.round(RR_std, 4),
        "SDSD": np.round(RR_sdsd, 4),
        "LF": np.round(lf, 4),
        "HF": np.round(hf, 4),
        "LHratio": np.round(LH_ratio, 4),
        "Heart Rate": np.round(heartRate),
        "Emotion": emotion
    }

    return result

def readRawData(t, y):
    # split time and value
    rawTimes, rawValues = np.array(t), np.array(y)
    rawRows, rawCols = len(t), 2
    rawDuration = (rawTimes[-1] - rawTimes[0]) / 1000  # ms to s
    rawFs = rawRows // rawDuration

    return rawTimes, rawValues, rawRows, rawCols, rawDuration, rawFs

def plot(filteredValues, peaks):
    fig, ax = plt.subplots()
    ax.plot(filteredValues)
    ax.plot(peaks, filteredValues[peaks], "xr")
    plt.show()

def process_ecg(t, y, should_plot=False):
    # read, process, and find peaks of ecg signal
    rawTimes, rawValues, rawRows, rawCols, rawDuration, rawFs = readRawData(t, y)
    ecgTimes, ecgValues, rows, duration, fs = interpolateRawSignal(rawTimes, rawValues, rawRows, rawDuration)
    filteredValues = filterEcgSignal(ecgValues, fs)
    peaks = findPeaks(filteredValues, fs)

    if should_plot:
        plot(filteredValues, peaks)
    parameters = getParameters(ecgTimes[peaks], peaks, rows, fs)
    return parameters

def ecg_filter(t, y):
    rawTimes, rawValues, rawRows, rawCols, rawDuration, rawFs = readRawData(t, y)
    ecgTimes, ecgValues, rows, duration, fs = interpolateRawSignal(rawTimes, rawValues, rawRows, rawDuration)
    filteredValues = filterEcgSignal(ecgValues, fs)
    return filteredValues

if __name__ == "__main__":
    path = sys.argv[1]
    t_points = []
    y_points = []
    with open(path, "r") as fin:
        for line in fin:
            a, b = line.rstrip().split(",")
            t_points.append(int(a))
            y_points.append(float(b))
    print(process_ecg(t_points, y_points, should_plot=True))