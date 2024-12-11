#include <WiFi.h>
#include <HTTPClient.h>
#include <Preferences.h>
#include <ArduinoOTA.h>
#include <pgmspace.h>

// Debug control - can be quickly disabled
#define DEBUG 1
#if DEBUG
    #define LOG(x) Serial.print(x)
    #define LOG_LN(x) Serial.println(x)
#else
    #define LOG(x)
    #define LOG_LN(x)
#endif

// Strings stored in flash memory
const char WIFI_SSID[] PROGMEM = "YOUR_WIFI_SSID";
const char WIFI_PASS[] PROGMEM = "YOUR_WIFI_PASSWORD";
const char SERVER_URL[] PROGMEM = "http://192.168.43.243:8080/api/devices/checkin";

#ifdef PROTO2_BOARD
    // Full board configuration
    struct PinConfig {
        uint8_t led[5] = {20, 26, 32, 23, 24};    // LED1-5
        uint8_t laser[2] = {28, 25};              // LASER1-2
        uint8_t servo[4] = {33, 34, 7, 13};       // SERVO1-4
        uint8_t ldr[5] = {9, 11, 10, 17, 8};      // LDR1-5
    };
    const char FW_VERSION[] PROGMEM = "1.0.0-proto2";
#else
    // Minimal dev board configuration
    struct PinConfig {
        uint8_t led[1] = {2};  // Just built-in LED
    };
    const char FW_VERSION[] PROGMEM = "1.1.1-dev";
#endif

PinConfig pins;

// Timing constants
const uint32_t CHECK_IN_INTERVAL = 30000;
uint32_t lastCheckin = 0;

// GUID storage
Preferences preferences;
String deviceGuid;

// Simple JSON string builder class
class JsonBuilder {
    private:
        String json;
    public:
        JsonBuilder() { json = "{"; }
        
        void addString(const char* key, const String& value) {
            if (json.length() > 1) json += ",";
            json += "\"" + String(key) + "\":\"" + value + "\"";
        }
        
        void startArray(const char* key) {
            if (json.length() > 1) json += ",";
            json += "\"" + String(key) + "\":[";
        }
        
        void addArrayString(const char* value, bool last = false) {
            json += "\"" + String(value) + "\"";
            if (!last) json += ",";
        }
        
        void endArray() {
            json += "]";
        }
        
        String close() {
            json += "}";
            return json;
        }
};

void setupPins() {
    #ifdef PROTO2_BOARD
        for(auto pin : pins.led) pinMode(pin, OUTPUT);
        for(auto pin : pins.laser) pinMode(pin, OUTPUT);
        for(auto pin : pins.ldr) pinMode(pin, INPUT);
        // Servos will be configured when needed
    #else
        pinMode(pins.led[0], OUTPUT);
    #endif
}

void setupWiFi() {
    WiFi.begin(WIFI_SSID, WIFI_PASS);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        LOG(".");
    }
    LOG_LN("\nWiFi Connected");
}

bool sendCheckin() {
    if (WiFi.status() != WL_CONNECTED) return false;

    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");

    JsonBuilder json;
    json.addString("guid", deviceGuid);
    json.addString("firmware_version", FW_VERSION);
    json.addString("ip_address", WiFi.localIP().toString());

    json.startArray("capabilities");
    #ifdef PROTO2_BOARD
        static const char* const CAPABILITIES[] PROGMEM = {
            "LED", "LASER", "SERVO", "LDR"
        };
        for(int i = 0; i < 4; i++) {
            json.addArrayString(CAPABILITIES[i], i == 3);
        }
    #else
        json.addArrayString("LED1", true);
    #endif
    json.endArray();

    String payload = json.close();
    LOG_LN(payload);

    int httpCode = http.POST(payload);
    bool success = false;
    
    if (httpCode > 0) {
        String response = http.getString();
        if (deviceGuid.isEmpty()) {
            int guidStart = response.indexOf("\"guid\":\"");
            if (guidStart > 0) {
                guidStart += 8; // length of "guid":"
                int guidEnd = response.indexOf("\"", guidStart);
                if (guidEnd > guidStart) {
                    deviceGuid = response.substring(guidStart, guidEnd);
                    preferences.putString("guid", deviceGuid);
                    LOG("New GUID: "); LOG_LN(deviceGuid);
                }
            }
        }
        success = true;
    }

    http.end();
    return success;
}

void setup() {
    #if DEBUG
        Serial.begin(115200);
    #endif
    
    setupPins();
    
    preferences.begin("laser-maze", false);
    deviceGuid = preferences.getString("guid", "");
    LOG("GUID: "); LOG_LN(deviceGuid);

    setupWiFi();
    sendCheckin();
}

void loop() {
    if (millis() - lastCheckin >= CHECK_IN_INTERVAL) {
        if (sendCheckin()) lastCheckin = millis();
    }

    #ifndef PROTO2_BOARD
        // Simple heartbeat for dev board
        static uint32_t lastBlink = 0;
        if (millis() - lastBlink >= 1000) {
            digitalWrite(pins.led[0], !digitalRead(pins.led[0]));
            lastBlink = millis();
        }
    #endif
}