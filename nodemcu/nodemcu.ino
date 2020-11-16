#include <ESP8266WiFi.h>
#include <SocketIoClient.h>
#include <SoftwareSerial.h>
#include <Adafruit_NeoPixel.h>

// user settings
#define NETWORK_NAME "mapuawifi"
#define NETWORK_PASSWORD "wala"
#define SERVER "192.168.0.22"
#define PORT 3000
#define SMS_NUMBER "AT+CMGS=\"+639215560333\""
#define BAUD_RATE 115200

#define SMS_DISCOMFORT_0 "no discomfort"
#define SMS_DISCOMFORT_1 "mild discomfort"
#define SMS_DISCOMFORT_2 "moderate discomfort"
#define SMS_DISCOMFORT_3 "severe discomfort"
const int LED_CONTROL = D2;

SocketIoClient socketio;
SoftwareSerial gsm_serial(D3, D4); // RX = D3, TX = D4
Adafruit_NeoPixel strip(1, LED_CONTROL);

void setup() {
  Serial.begin(BAUD_RATE);
  Serial.flush();

  // connect to WiFi network
  WiFi.begin(NETWORK_NAME, NETWORK_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
    
  // initialize RGB LED
  strip.begin();
  strip.show();
  
  //initialize gsm
  gsm_serial.begin(BAUD_RATE);
  gsm_serial.flush();

  // connect to server
  socketio.begin(SERVER, PORT);
  socketio.on("output-nodemcu", on_receive_discomfort_level);
}

void loop() {
  socketio.loop();
  while (!Serial.available()) {
    Serial.write('r');
  }
  read_and_send_data();
  Serial.flush();
}

void read_and_send_data() {
  String signal_value = "\"" + Serial.readStringUntil('\n') + "\"";
  // log
  //Serial.println(signal_value);
  socketio.emit("signal-nodemcu", signal_value.c_str());
}

void on_receive_discomfort_level(const char* payload, size_t len) {
  // parse discomfort level
  int discomfort_level = *payload - '0';
  
  // set sms message and LED color
  String sms_message;
  switch(discomfort_level) {
    case 0:
      sms_message = SMS_DISCOMFORT_0;
      strip.setPixelColor(0, 0, 255, 0);
      strip.show();
      break;
    case 1:
      sms_message = SMS_DISCOMFORT_1;
      strip.setPixelColor(0, 255, 255, 0);
      strip.show();
      break;
    case 2:
      sms_message = SMS_DISCOMFORT_2;
      strip.setPixelColor(0, 255, 128, 0);
      strip.show();
      break;
    case 3:
      sms_message = SMS_DISCOMFORT_3;
      strip.setPixelColor(0, 255, 0, 0);
      strip.show();
      break;
    default:
      break;
  }
  //log
  //Serial.println(sms_message);
  send_sms(sms_message);
}

void send_sms(String sms_message) {
  gsm_serial.println("AT");
  gsm_serial_wait();
  gsm_serial.println("AT+CMGF=1");
  gsm_serial_wait();
  gsm_serial.println(SMS_NUMBER);
  gsm_serial_wait();
  gsm_serial.print(sms_message);
  gsm_serial_wait();
  gsm_serial.write(26);
}

void gsm_serial_wait() {
  delay(500);
  while (gsm_serial.available())
    Serial.print(gsm_serial.read());
  Serial.println();
  Serial.flush();
}