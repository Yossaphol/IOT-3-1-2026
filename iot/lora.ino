#include <lmic.h>
#include <hal/hal.h>
#include <SPI.h>

// ---- ค่าจาก ChirpStack (DevEUI/JoinEUI แบบ LSB, AppKey แบบ MSB ตามเอกสาร) ----
static const u1_t PROGMEM APPEUI[8] = { 0xB9, 0x80, 0x66, 0x76, 0xE4, 0x0B, 0xE6, 0x44 };
void os_getArtEui (u1_t* buf) { memcpy_P(buf, APPEUI, 8); }
static const u1_t PROGMEM DEVEUI[8] = { 0xC1, 0x30, 0x80, 0xD2, 0x9A, 0x1C, 0xA8, 0x75 };
void os_getDevEui (u1_t* buf) { memcpy_P(buf, DEVEUI, 8); }
static const u1_t PROGMEM APPKEY[16] = { 0xF5, 0x0F, 0xF8, 0x7B, 0x2F, 0xD3, 0x33, 0x51,
                                         0x76, 0xD5, 0xA1, 0xFF, 0xCA, 0xF7, 0xCD, 0xD1 };
void os_getDevKey (u1_t* buf) { memcpy_P(buf, APPKEY, 16); }

// ---- LDR ----
const int LIGHT_AO_PIN = A0;
const int LIGHT_DO_PIN = 4;        // 1 = มืด, 0 = สว่าง

const unsigned TX_INTERVAL = 30;   // วินาที
static uint8_t mydata[3];          // [AO hi][AO lo][DO]
static osjob_t sendjob;

const lmic_pinmap lmic_pins = {
    .nss = 10,
    .rxtx = LMIC_UNUSED_PIN,
    .rst = 7,
    .dio = {2, 5, 6},
};

void packPayload() {
    uint16_t raw = analogRead(LIGHT_AO_PIN);
    mydata[0] = raw >> 8;
    mydata[1] = raw & 0xFF;
    mydata[2] = digitalRead(LIGHT_DO_PIN) == HIGH ? 1 : 0;
    Serial.print(F("AO raw = ")); Serial.print(raw);
    Serial.print(F("  light = ")); Serial.print((1023 - raw) * 100.0 / 1023.0, 1);
    Serial.print(F(" %  DO = ")); Serial.println(mydata[2]);
}

void onEvent (ev_t ev) {
    switch (ev) {
        case EV_JOINING:
            Serial.println(F("EV_JOINING"));
            break;
        case EV_JOINED:
            Serial.println(F("EV_JOINED"));
            LMIC_setLinkCheckMode(0);
            break;
        case EV_JOIN_FAILED:
            Serial.println(F("EV_JOIN_FAILED"));
            break;
        case EV_TXCOMPLETE:
            Serial.println(F("EV_TXCOMPLETE"));
            os_setTimedCallback(&sendjob, os_getTime() + sec2osticks(TX_INTERVAL), do_send);
            break;
        default:
            break;
    }
}

void do_send(osjob_t* j) {
    if (LMIC.opmode & OP_TXRXPEND) {
        Serial.println(F("OP_TXRXPEND, not sending"));
    } else {
        packPayload();
        LMIC_setTxData2(1, mydata, sizeof(mydata), 0);
        Serial.println(F("Packet queued"));
    }
}

void setup() {
    Serial.begin(9600);
    Serial.println(F("Starting"));
    pinMode(LIGHT_DO_PIN, INPUT);

    os_init();
    LMIC_reset();
    LMIC_setupChannel(0, 923200000, DR_RANGE_MAP(DR_SF12, DR_SF7), BAND_CENTI);
    LMIC_setDrTxpow(DR_SF12, 14);
    do_send(&sendjob);
}

void loop() {
    os_runloop_once();
}