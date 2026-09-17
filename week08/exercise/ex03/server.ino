#include <WiFiS3.h>
#include <WiFiUdp.h>
#include <coap-simple.h>

// ========================================
// WiFi
// ========================================

const char WIFI_SSID[] = "yossaphol";
const char WIFI_PASSWORD[] = "123456789";

// ========================================
// CoAP
// ========================================

const uint16_t COAP_PORT = 5683;

WiFiUDP udp;
Coap coap(udp);

// ========================================
// Potentiometer
// ========================================

#define POT_PIN A0

int lastValue = -1;

unsigned long lastReadTime = 0;
const unsigned long READ_INTERVAL = 100;


// ========================================
// Connect WiFi
// ========================================

void connectWiFi() {

  Serial.println();
  Serial.print("Connecting to WiFi: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  int retry = 0;

  while (WiFi.status() != WL_CONNECTED) {

    delay(500);

    Serial.print(".");

    retry++;

    // ถ้าเกิน 30 ครั้ง ให้ลอง begin ใหม่
    if (retry >= 30) {

      Serial.println();
      Serial.println("WiFi connection failed. Retrying...");

      WiFi.disconnect();
      delay(1000);

      WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

      retry = 0;
    }
  }

  Serial.println();
  Serial.println("WiFi connected!");

  // รอ DHCP แจก IP
  delay(1000);

  Serial.print("Arduino IP: ");
  Serial.println(WiFi.localIP());

  Serial.print("Gateway: ");
  Serial.println(WiFi.gatewayIP());

  Serial.print("Subnet: ");
  Serial.println(WiFi.subnetMask());
}


// ========================================
// CoAP GET /potentiometer
// ========================================

void handlePotentiometer(
  CoapPacket &packet,
  IPAddress ip,
  int port
) {

  int rawValue = analogRead(POT_PIN);

  char payload[10];

  sprintf(payload, "%d", rawValue);


  // ======================================
  // Observe Request
  // ======================================

  if (packet.isObserve()) {

    uint32_t observeValue = 0;

    packet.getObserveValue(observeValue);

    Serial.println();
    Serial.println("================================");
    Serial.println("Observe Request received");
    Serial.print("Client IP: ");
    Serial.println(ip);
    Serial.print("Client Port: ");
    Serial.println(port);
    Serial.print("Observe value: ");
    Serial.println(observeValue);


    // Observe = 0
    // Register observer
    if (observeValue == 0) {

      bool added = coap.addObserver(
        "potentiometer",
        ip,
        port,
        packet.token,
        packet.tokenlen
      );

      if (added) {

        Serial.println("Observer registered!");

        // ส่ง response แรกพร้อม Observe option
        coap.sendObserveResponse(
          ip,
          port,
          packet.messageid,
          payload,
          strlen(payload),
          COAP_CONTENT,
          COAP_TEXT_PLAIN,
          packet.token,
          packet.tokenlen,
          0
        );

      } else {

        Serial.println("Failed to register observer");

        coap.sendResponse(
          ip,
          port,
          packet.messageid,
          "Observer full"
        );
      }
    }

    // Observe = 1
    // Cancel Observe
    else if (observeValue == 1) {

      coap.removeObserver(
        "potentiometer",
        ip,
        port,
        packet.token,
        packet.tokenlen
      );

      Serial.println("Observer removed!");

      coap.sendResponse(
        ip,
        port,
        packet.messageid,
        payload
      );
    }

    Serial.println("================================");
  }


  // ======================================
  // Normal GET
  // ======================================

  else {

    Serial.print("GET /potentiometer -> ");
    Serial.println(rawValue);

    coap.sendResponse(
      ip,
      port,
      packet.messageid,
      payload
    );
  }
}


// ========================================
// SETUP
// ========================================

void setup() {

  Serial.begin(115200);

  delay(1000);

  Serial.println();
  Serial.println("================================");
  Serial.println("Arduino CoAP Server");
  Serial.println("================================");


  // --------------------------------------
  // Potentiometer
  // --------------------------------------

  pinMode(POT_PIN, INPUT);


  // --------------------------------------
  // WiFi
  // --------------------------------------

  connectWiFi();


  // --------------------------------------
  // CoAP
  // --------------------------------------

  coap.server(
    handlePotentiometer,
    "potentiometer"
  );

  coap.start(COAP_PORT);


  Serial.println();
  Serial.println("================================");
  Serial.println("CoAP Server Started");
  Serial.print("Arduino IP : ");
  Serial.println(WiFi.localIP());
  Serial.println("Port       : 5683");
  Serial.println("Resource   : /potentiometer");
  Serial.println("Observe    : Supported");
  Serial.println("================================");
}


// ========================================
// LOOP
// ========================================

void loop() {

  // --------------------------------------
  // ต้องเรียกบ่อย ๆ เพื่อรับ CoAP request
  // --------------------------------------

  coap.loop();


  // --------------------------------------
  // อ่าน Potentiometer
  // --------------------------------------

  if (millis() - lastReadTime >= READ_INTERVAL) {

    lastReadTime = millis();

    int rawValue = analogRead(POT_PIN);


    // แสดงค่าเมื่อค่าเปลี่ยน
    if (rawValue != lastValue) {

      lastValue = rawValue;

      Serial.print("Potentiometer: ");
      Serial.println(rawValue);


      // ------------------------------------
      // ส่ง Observe Notification
      // ------------------------------------

      char payload[10];

      sprintf(payload, "%d", rawValue);

      int sent = coap.notify(
        "potentiometer",
        payload,
        strlen(payload),
        COAP_TEXT_PLAIN
      );

      if (sent > 0) {

        Serial.print("Observe notification sent: ");
        Serial.println(rawValue);
      }
    }
  }

}