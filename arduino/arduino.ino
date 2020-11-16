// pins
const int ECG_PIN = A0;
const int GSR_PIN = A1;
const int PM_PIN = A2;
const int WM_PIN = A3;
const int PM_SELECT_ROWS[3] = {4, 3, 2};
const int PM_SELECT_COLUMNS[3] = {7, 6, 5};
const int WM_SELECT_ROWS[3] = {10, 9, 8};
const int WM_SELECT_COLUMNS[3] = {13, 12, 11};
const int READY_LED = A4;

// mux/demux select bits
const int SELECT_BITS[8][3] = {
  {0, 0, 0},
  {0, 0, 1},
  {0, 1, 0},
  {0, 1, 1},
  {1, 0, 0},
  {1, 0, 1},
  {1, 1, 0},
  {1, 1, 1}
};

const int DELAY = 10;
const int NUM_MATRIX_CALIBRATIONS = 300;
int PM_OFFSETS[8][8];
int WM_OFFSETS[8][8];
#define BAUD_RATE 115200

void setup() {
  Serial.begin(BAUD_RATE);
  Serial.flush();

  // initialize matrix sensor pins
  for (int i = 2; i <= 13; i++) {
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }
  pinMode(PM_PIN, INPUT);
  pinMode(WM_PIN, INPUT);
  pinMode(ECG_PIN, INPUT);
  pinMode(GSR_PIN, INPUT);
  pinMode(READY_LED, OUTPUT);
  digitalWrite(READY_LED, LOW);
  matrix_calibration();
  digitalWrite(READY_LED, HIGH);
}

void loop() {
  for (int i = 0; i < 8; i++) {
    set_mux(i, PM_SELECT_ROWS);
    set_mux(i, WM_SELECT_ROWS);
    for (int j = 0; j < 8; j++) {
      set_mux(j, PM_SELECT_COLUMNS);
      set_mux(j, WM_SELECT_COLUMNS);
      int pm_value = analogRead(PM_PIN) - PM_OFFSETS[i][j];
      int wm_value = analogRead(WM_PIN) - WM_OFFSETS[i][j];
      //int pm_value = analogRead(PM_PIN);
      //int wm_value = analogRead(WM_PIN);
      String pm_signal = "pm:" + String(i) + "," + String(j) + "," + String(pm_value) + "\n";
      String wm_signal = "wm:" + String(i) + "," + String(j) + "," + String(wm_value) + "\n";
      ack();
      Serial.print(pm_signal);
      Serial.print(wm_signal);
      ecg();
      gsr();
      delay(DELAY);
    }  
  }
}

void set_mux(int selected_pin, int* select_pins) {
    for(int i = 0; i < 3; select_pins++, i++) {
      digitalWrite(*select_pins, SELECT_BITS[selected_pin][i]);
    }
}

void ecg() {
  int raw_ecg = analogRead(ECG_PIN);
  String ecg_signal = "ecg:" + String(raw_ecg) + "\n";
  Serial.print(ecg_signal); 
}

void gsr() {
  int raw_gsr = analogRead(GSR_PIN);
  String gsr_signal = "gsr:" + String(raw_gsr) + "\n";
  Serial.print(gsr_signal);
}

int ack() {
  while (1) {
    // wait for a message from Serial
    while (!Serial.available()) {
      ;
    }

    char message = Serial.read();
    if (message == 'r') {
      break;  
    }
  }

  // flush buffer to get rid of excess 'r'
  Serial.flush();
}

void matrix_calibration() {
  for (int n = 0; n < NUM_MATRIX_CALIBRATIONS; n++) {
    for (int i = 0; i < 8; i++) {
      set_mux(i, PM_SELECT_ROWS);
      set_mux(i, WM_SELECT_ROWS);
      for (int j = 0; j < 8; j++) {
        set_mux(j, PM_SELECT_COLUMNS);
        set_mux(j, WM_SELECT_COLUMNS);
        PM_OFFSETS[i][j] += analogRead(PM_PIN);
        WM_OFFSETS[i][j] += analogRead(WM_PIN);
      }
    }
  }

  for (int i = 0; i < 8; i++) {
    for (int j = 0; j < 8; j++) {
      PM_OFFSETS[i][j] /= NUM_MATRIX_CALIBRATIONS;
      WM_OFFSETS[i][j] /= NUM_MATRIX_CALIBRATIONS;
    }  
  }
}