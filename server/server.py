import socketio
import eventlet
import time, sys

# CONSTANTS
GSR_CONSTANT = 10000 # 10000 according to seedstudio
EPSILON = 1e-22 # used to prevent numerical divide by zero errors

sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)
should_record = False
should_log = False

# @sio.on("connect")
# def on_connect(sid, environ):
#     time.sleep(5)
#     sio.emit("request-discomfort-level", "")
#     sio.emit("receive-inference", "69:69pm,Severe")

# @sio.on("discomfort-level")
# def recieve_discomfort_level(sid, data):
#     print(data)

@sio.on("ecg")
def receive_ecg(sid, ecg):
    ecg = float(ecg)
    handle_data("ecg", ecg)

@sio.on("gsr")
def receive_gsr(sid, gsr):
    gsr = float(gsr)
    gsr = get_skin_conductance(gsr)
    handle_data("gsr", gsr)

def handle_data(data_type, data):
    current_time = get_time()

    # logging
    if should_record:
        record_values(current_time, data, f"./{data_type}.samples")
    if should_log:
        print(f"{data_type}:{current_time},{data}")

    # send data to mobile
    sio.emit(f"mobile-{data_type}-signal", f"{get_time()},{data}")

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

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for param in sys.argv[1:]:
            if param.lower() == "log":
                should_log = True
            elif param.lower() == "record":
                should_record = True
    eventlet.wsgi.server(eventlet.listen(('', 3000)), app)
