from absl import app
from absl import flags
import socketio
import eventlet
import time, sys
from utils.logger import Logger
from signal_processing.wheelchair_signals_monitor import Wheelchair_Signals_Monitor
from db.DbContext import DbContext
from bson.objectid import ObjectId
from models.ECG import ECG
from models.GSR import GSR
from models.MatrixItem import MatrixItem
from models.Record import Record
from utils.matrix import Matrix
from datetime import datetime
from neural_network.model import load_model
import numpy as np
import pandas as pd
from datetime import datetime

# CONSTANTS
GSR_CONSTANT = 10000 # used in computing the skin conductance (10000 according to seedstudio)
EPSILON = 1e-22 # used to prevent numerical divide by zero errors
SIGNAL_SET = {"ecg", "gsr", "pm", "wm"} # signals not in this set are discarded
DB_PASSWORD = "RYHUNEPzmAlsE5VT"
DB_USERNAME = "user_1"
CLASSES = ["No Discomfort", "Mild Discomfort", "Moderate Discomfort", "Severe Discomfort"]
NUM_FEATURES = 111
PRESSURE_THRESHOLD = 16 
WETNESS_THRESHOLD = 70

# flags
FLAGS = flags.FLAGS
flags.DEFINE_list("log_set", "", "set of tags to log")
flags.DEFINE_boolean("record", True, "record samples")
flags.DEFINE_enum("mode", "data_gathering", "[inference, data_gathering]",
                  "inference: predict using model, "
                  "data_gathering: save data to database")

# server initializations
sio = socketio.Server(cors_allowed_origins="*")
server = socketio.WSGIApp(sio)
logger = Logger()
signal_monitor = Wheelchair_Signals_Monitor(duration_per_compute=120e3, pressure_threshold=PRESSURE_THRESHOLD, wetness_threshold=WETNESS_THRESHOLD)
context = DbContext(DB_USERNAME, "wheelchairDB", DB_PASSWORD)
model = load_model(NUM_FEATURES, "./neural_network/model.hdf5")

# @sio.event
# def connect(sid, environ):    
#     print("hello")
#     sio.emit("no-user-detected", "no user detected")

# @sio.on("gg")
# def pong(sid, data):
#     print(data)
#     sio.emit("output-mobile", f"{datetime.now()},No Discomfort")

@sio.on("signal-nodemcu")
def receive_signal(sid, data):
    # parse data
    data = data.split(":")

    # assert data integrity
    if len(data) != 2:
        return
    if not all(list(map(len, data))):
        return
    signal_type, signal = data

    # discard signals not in SIGNAL_SET
    if signal_type not in SIGNAL_SET:
        return

    # handle signal
    if signal_type == "pm" or signal_type == "wm":
        signal = list(map(int, signal.split(",")))
        # assert data integrity
        if len(signal) != 3:
            return
        if signal[2] < 0: signal[2] = 0

    else:
        signal = float(signal)
        # if signal_type == "gsr":
        #     signal = get_skin_conductance(signal)

    handle_data(signal_type, signal)

def handle_data(signal_type, signal):
    current_time = get_time()

    logger.log(signal_type, f"{signal_type}:{current_time},{signal}")
        
    # send signal to mobile
    sio.emit(f"mobile-{signal_type}-signal", f"{get_time()},{signal}")

    # send the signal to the signal monitor
    has_features = signal_monitor.add_point(signal_type=signal_type, t=current_time, y=signal)
    if has_features == 1:
        if FLAGS.mode == "inference":
            # use model to predict
            x = preprocess_data()
            prediction = np.argmax(model(x))
            predicted_class = CLASSES[prediction]
            logger.log("inference", predicted_class)
            # send prediction to nodemcu
            sio.emit("output-nodemcu", f"{prediction}")
            # send prediction to mobile
            sio.emit("output-mobile", f"{datetime.now()},{predicted_class}")
        elif FLAGS.mode == "data_gathering":
            # request discomfort level from the mobile app
            sio.emit("request-discomfort-level", "")
        sio.emit("user-detected", "user detected")
    elif has_features == 2:
        # no user detected
        logger.log("user_detected", "no user detected")
        sio.emit("no-user-detected", f"{datetime.now()},Severe Discomfort")
    elif has_features == 3: sio.emit("user-detected", "user detected")


@sio.on("discomfort-level")
def recieve_discomfort_level(sid, data):
    logger.log("features", signal_monitor.features)
    discomfort_level = data
    logger.log("discomfort_level", data)

    ecg_features = signal_monitor.features["ecg"]
    ecg_model = ECG(
        mean_rri = ecg_features["Mean RRI"],
        cvrr = ecg_features["CVRR"],
        sdrr = ecg_features["SDRR"],
        sdsd = ecg_features["SDSD"],
        lf = ecg_features["LF"],
        hf = ecg_features["HF"],
        ratio = ecg_features["LHratio"],
        heart_rate = ecg_features["Heart Rate"]
    )
    gsr_features = signal_monitor.features["gsr"]
    gsr_model = GSR(
        mini = gsr_features["min"],
        maxi = gsr_features["max"],
        mean = gsr_features["mean"],
        median = gsr_features["median"],
        std = gsr_features["std"],
        variance = gsr_features["variance"]
    )
    pm_features = signal_monitor.features["pm"]
    wm_features = signal_monitor.features["wm"]
    time_id = signal_monitor.features["time_id"]
    
    record = Record()
    record.time_id = time_id
    record.ecg = ecg_model
    record.gsr = gsr_model
    record.pressure_matrix = pm_features
    record.wetness_matrix = wm_features
    record.discomfort_level = discomfort_level
    inserted_id = context.records.insert_one(record)
  

def get_skin_conductance(gsr_value):
    # equation from https://wiki.seeedstudio.com/Grove-GSR_Sensor/
    resistance = ((1024 + 2.0 * gsr_value) * GSR_CONSTANT) / ((512 - gsr_value) + EPSILON)
    # conductance is the reciprocal of resistance
    conductance = (1 / resistance) * 1e6
    return conductance

def get_time():
    reference_time = time.localtime(time.time())
    reference_time = time.mktime((
        reference_time.tm_year, reference_time.tm_mon, reference_time.tm_mday, 
        0, 0, 0, 
        reference_time.tm_wday, reference_time.tm_yday, reference_time.tm_isdst
    ))
    millis_today = int((time.time() - reference_time) * 1000)
    return millis_today

def main(argv):
    logger.log_set = set(FLAGS.log_set)
    print(f"mode: {FLAGS.mode}")
    eventlet.wsgi.server(eventlet.listen(('', 3000)), server)


def vardump(obj, title=None):
  if title: print(f"==> {title}\n----------")
  print(vars(obj))
  print()

def preprocess_data():
    corr_df = pd.read_csv("./neural_network/correlation.csv")
    feature_names = list(corr_df)[2:NUM_FEATURES+2]

    ecg_features = signal_monitor.features["ecg"]
    gsr_features = signal_monitor.features["gsr"]
    pm_features = signal_monitor.features["pm"]
    wm_features = signal_monitor.features["wm"]

    features_dict = {
        "mean_rri":[ecg_features["Mean RRI"]],
        "cvrr":[ecg_features["CVRR"]],
        "sdrr":[ecg_features["SDRR"]],
        "sdsd":[ecg_features["SDSD"]],
        "lf":[ecg_features["LF"]],
        "hf":[ecg_features["HF"]],
        "ratio":[ecg_features["LHratio"]],
        "heart_rate":[ecg_features["Heart Rate"]],
        "mini":[gsr_features["min"]],
        "maxi":[gsr_features["max"]],
        "mean":[gsr_features["mean"]],
        "median":[gsr_features["median"]],
        "std":[gsr_features["std"]],
        "variance":[gsr_features["variance"]]
    }
    for row in range(8):
        for col in range(8):
            features_dict[f"pressure_matrix_{row}_{col}"] = [pm_features[row][col]]
            features_dict[f"wetness_matrix_{row}_{col}"] = [wm_features[row][col]]

    features_df = pd.DataFrame(data=features_dict)
    features_df = features_df[feature_names]
    x = features_df.to_numpy()
    return x

def test():
    ecg_features = {
        "Mean RRI": 1194.6336,
        "CVRR": 43.0046,
        "SDRR": 513.7475,
        "SDSD": 438.5067,
        "LF": 769.0859,
        "HF": 1294.4461,
        "LHratio": 0.5941,
        "Heart Rate": 50,
    }
    gsr_features = {
        "max": 491,
        "min": 48.2,
        "mean": 473.993218,
        "median": 474.65,
        "std": 11.26413919,
        "variance": 126.8808318
    }
    pm_features = [[0 for __ in range(8)] for _ in range(8)]
    wm_features = [[0 for __ in range(8)] for _ in range(8)]

    signal_monitor.features["ecg"] = ecg_features
    signal_monitor.features["gsr"] = gsr_features
    signal_monitor.features["pm"] = pm_features
    signal_monitor.features["wm"] = wm_features
    x = preprocess_data()
    res = model(x)
    print(CLASSES[np.argmax(res)])

if __name__ == "__main__":
    # test()
    app.run(main)

    # ------------------------------- DB SAMPLE CODE ------------------------------------------------
    # context = DbContext("WheelchairMonitoring", "wheelchair")

    # # 1) Creating ECG Model
    # ecg = ECG(mean_rri=1, cvrr=2, sdrr=3, sdsd=4, lf=5, hf=6, ratio=7, heart_rate=8)
    # vardump(ecg, "ECG")

    # # 2) Creating GSR Model
    # gsr = GSR(mini=1, maxi=2, mean=3, median=4, std=5, variance=6)
    # vardump(gsr, "GSR")

    # # 3) Creating an 8x8 matrix (utils/matrix.py)
    # # Pressure
    # raw_pressure_matrix = Matrix.RandomMatrix(8)
    # Matrix.PrintMatrix(raw_pressure_matrix, "Raw Pressure Matrix")

    # # Raw 2d pressure_matrix to PressureMatrix object
    # pressure_matrix = Matrix.ToMatrixItems(raw_pressure_matrix)
    # Matrix.PrintItems(pressure_matrix, title="Pressure Matrix Items")

    # # Wetness
    # raw_wetness_matrix = Matrix.RandomMatrix(8)
    # Matrix.PrintMatrix(raw_wetness_matrix, "Raw Wetness Matrix")

    # # Raw 2d wetness_matrix to WetnessMatrix object
    # wetness_matrix = Matrix.ToMatrixItems(raw_wetness_matrix)
    # Matrix.PrintItems(wetness_matrix, title="Wetness Matrix Items")

    # # 4) Creating a Record
    # record = Record()

    # # Record - Example Time
    # record.time_started =  datetime.now().timestamp()
    # record.time_finished = datetime.now().replace(minute=59, second=59, microsecond=696969).timestamp()
    
    # # Record - Add other properties
    # record.ecg = ecg
    # record.gsr = gsr
    # record.pressure_matrix = pressure_matrix
    # record.wetness_matrix = wetness_matrix

    # # 5) Inserting record to db
    # inserted_id = context.records.insert_one(record)
    # # Uncomment to view all data of the record
    # # record.dump("to Insert")

    # # 6) Finding a record in db
    # print(inserted_id)
    # found_record = context.records.find_by_id(inserted_id)
    # # Uncomment to view all data of the record
    # # found_record.dump("Found")
