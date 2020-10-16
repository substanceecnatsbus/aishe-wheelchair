// pins
const int GSR_PIN = A1;
const int ECG_PIN = A0;
const int DELAY = 5;
const unsigned long BAUD_RATE = 115200;
const int NUM_AVERAGE = 10;

long gsr_sum = 0;
int i = 0;

void setup() {
  Serial.begin(BAUD_RATE);
  Serial.flush();
}

void loop() {
  int raw_ecg = analogRead(ECG_PIN);
  Serial.println("ecg:" + String(raw_ecg));
  
  read_gsr();

  i = ++i % NUM_AVERAGE;
  delay(DELAY);
}

void read_gsr() {
  int raw_gsr = analogRead(GSR_PIN);
  gsr_sum += raw_gsr;
  if (i == 0) {
    int gsr_average = gsr_sum / NUM_AVERAGE;
    Serial.println("gsr:" + String(gsr_average));
    gsr_sum = 0;
  }
}
