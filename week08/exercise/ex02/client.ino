#include <WiFiS3.h>
#include <coap-simple.h>

char ssid[] = "yossaphol";
char pass[] = "123456789";

IPAddress serverIP(172, 20, 10, 2);

#define COAP_PORT 5683
#define POT_PIN A0

WiFiUDP udp;
Coap coap(udp, COAP_PORT);


// ===============================
// CoAP Response Callback
// ===============================
void responseCallback(CoapPacket &packet, IPAddress ip, int port) {
  Serial.println("CoAP Response received");
}


// ===============================
// SETUP
// ===============================
void setup() {

  Serial.begin(9600);

  // Connect WiFi
  Serial.print("Connecting to WiFi");

  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi connected!");

  Serial.print("Arduino IP: ");
  Serial.println(WiFi.localIP());

  // CoAP
  coap.response(responseCallback);
  coap.start();

  Serial.println("CoAP Client Started");
}


// ===============================
// LOOP
// ===============================
void loop() {

  // อ่านค่าจาก Potentiometer
  int rawValue = analogRead(POT_PIN);

  // แปลง 0-1023 → 0-100
  int brightness = map(rawValue, 0, 1023, 0, 100);

  // แปลงเป็น String
  char payload[10];
  sprintf(payload, "%d", brightness);

  // แสดงค่าทาง Serial Monitor
  Serial.print("Potentiometer: ");
  Serial.print(rawValue);

  Serial.print("  Brightness: ");
  Serial.println(brightness);

  // ส่งค่าไป Raspberry Pi
  coap.put(
    serverIP,
    COAP_PORT,
    "led",
    payload,
    strlen(payload)
  );

  coap.loop();

  delay(1000);
}