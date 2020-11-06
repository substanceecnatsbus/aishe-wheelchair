#include <ESP8266WiFi.h>
#include <SocketIoClient.h>
#include <ctype.h>

// user settings
#define NETWORK_NAME "xxx"
#define NETWORK_PASSWORD "xxx"
#define SERVER "192.168.0.14"
#define PORT 3000

#define BAUD_RATE 115200

SocketIoClient socketio;

void setup() {
  Serial.begin(BAUD_RATE);
  Serial.flush();

  // connect to WiFi network
  WiFi.begin(NETWORK_NAME, NETWORK_PASSWORD);
  while (WiFi.status() != WL_CONNECTED)
    delay(500); 

  // connect to server
  socketio.begin(SERVER, PORT);
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
  Serial.println(signal_value);
  socketio.emit("signal-nodemcu", signal_value.c_str());
}
