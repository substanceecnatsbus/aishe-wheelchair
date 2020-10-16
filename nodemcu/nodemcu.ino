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

  if (Serial.available()) {
    read_and_send_data();
  }
}

void read_and_send_data() {
  String raw_input = Serial.readStringUntil('\n');
  int n = raw_input.length() - 1;
  
  char key_val[2][8];
  key_val[1][0] = '"';
  char current_char;
  int i = 0, j = 0, k = 0;

  while (i < n) {
    current_char = raw_input[i++];
    if (isalnum(current_char)) {
      key_val[j][k++] = current_char;
    } else if (current_char == ':') {
      key_val[j][k] = '\0';
      ++j;
      k = 1;
    }
  }
  key_val[1][k++] = '"';
  key_val[1][k] = '\0';

  Serial.println(key_val[0]);
  Serial.println(key_val[1]);
  socketio.emit(key_val[0], key_val[1]);
}
