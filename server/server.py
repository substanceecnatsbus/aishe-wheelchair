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

# CONSTANTS
GSR_CONSTANT = 10000 # used in computing the skin conductance (10000 according to seedstudio)
EPSILON = 1e-22 # used to prevent numerical divide by zero errors
SIGNAL_SET = {"ecg", "gsr", "pm", "wm"}

# abseil flags
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
signal_monitor = Wheelchair_Signals_Monitor()
current_features = None

# @sio.on("connect")
# def on_connect(sid, environ):
#     time.sleep(5)
#     sio.emit("request-discomfort-level", "")
#     sio.emit("receive-inference", "69:69pm,Severe")

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
        if signal[2] < 0: signal[2] = 0
        # assert data integrity
        if len(signal) != 3:
            return
    else:
        signal = float(signal)
        if signal_type == "gsr":
            signal = get_skin_conductance(signal)

    handle_data(signal_type, signal)

def handle_data(signal_type, signal):
    current_time = get_time()

    logger.log(signal_type, f"{signal_type}:{current_time},{signal}")
        
    # send signal to mobile
    sio.emit(f"mobile-{signal_type}-signal", f"{get_time()},{signal}")

    # send the signal to the signal monitor
    features = signal_monitor.add_point(signal_type=signal_type, t=current_time, y=signal)
    if features != None:
        logger.log("features", features)
        # RECORD VALUES
        if FLAGS.mode == "inference":
            # # use model to predict
            # prediction = model.predict(features)
            # logger.log("inference", prediction)
            # # send prediction to server
            # sio.emit("receive-inference", f"{current_time},{prediction}")
            pass
        elif FLAGS.mode == "data_gathering":
            current_features = features
            # request discomfort level from the mobile app
            sio.emit("request-discomfort-level", "")


@sio.on("discomfort-level")
def recieve_discomfort_level(sid, data):
    discomfort_level = data
    logger.log("discomfort-level", data)
    # save current_feaures and discomfort_level to database
    

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

def record_values(t, y, path_to_samples):
    with open(path_to_samples, "a") as fout:
        fout.write(f"{t},{y}\n")

def main(argv):
    logger.log_set = set(FLAGS.log_set)
    eventlet.wsgi.server(eventlet.listen(('', 3000)), server)


def vardump(obj, title=None):
  if title: print(f"==> {title}\n----------")
  print(vars(obj))
  print()

if __name__ == "__main__":
    # app.run(main)
    context = DbContext()

    # 1) Creating ECG Model
    ecg = ECG(mean_rri=1, cvrr=2, sdrr=3, sdsd=4, lf=5, hf=6, ratio=7, heart_rate=8)
    vardump(ecg, "ECG")

    # 2) Creating GSR Model
    gsr = GSR(mini=1, maxi=2, mean=3, median=4, std=5, variance=6)
    vardump(gsr, "GSR")

    # 3) Creating an 8x8 matrix (utils/matrix.py)
    # Pressure
    raw_pressure_matrix = Matrix.RandomMatrix(8)
    Matrix.PrintMatrix(raw_pressure_matrix, "Raw Pressure Matrix")

    # Raw 2d pressure_matrix to PressureMatrix object
    pressure_matrix = Matrix.ToMatrixItems(raw_pressure_matrix)
    Matrix.PrintItems(pressure_matrix, title="Pressure Matrix Items")

    # Wetness
    raw_wetness_matrix = Matrix.RandomMatrix(8)
    Matrix.PrintMatrix(raw_wetness_matrix, "Raw Wetness Matrix")

    # Raw 2d wetness_matrix to WetnessMatrix object
    wetness_matrix = Matrix.ToMatrixItems(raw_wetness_matrix)
    Matrix.PrintItems(wetness_matrix, title="Wetness Matrix Items")

    # 4) Creating a Record
    record = Record()

    # Record - Example Time
    record.time_started =  datetime.now().timestamp()
    record.time_finished = datetime.now().replace(minute=59, second=59, microsecond=696969).timestamp()
    
    # Record - Add other properties
    record.ecg = ecg
    record.gsr = gsr
    record.pressure_matrix = pressure_matrix
    record.wetness_matrix = wetness_matrix

    # 5) Inserting record to db
    inserted_id = context.records.insert_one(record)
    # Uncomment to view all data of the record
    # record.dump("to Insert")

    # 6) Finding a record in db
    print(inserted_id)
    found_record = context.records.find_by_id(inserted_id)
    # Uncomment to view all data of the record
    # found_record.dump("Found")
