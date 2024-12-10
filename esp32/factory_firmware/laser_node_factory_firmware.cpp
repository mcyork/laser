#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <ArduinoOTA.h>

// Enable debug logs
#define DEBUG 1

#ifdef DEBUG
    #define LOG(x) Serial.print(x)
    #define LOG_LN(x) Serial.println(x)
#else
    #define LOG(x)
    #define LOG_LN(x)
#endif

// Board Configuration
#ifdef PROTO2_BOARD
    const int LED1_PIN = 20;  // IO16
    const int LED2_PIN = 26;  // IO26
    const int LED3_PIN = 32;  // IO36
    const int LED4_PIN = 23;  // IO19
    const int LED5_PIN = 24;  // IO20 (Power LED)
    const int LASER1_PIN = 28;  // IO33
    const int LASER2_PIN = 25;  // IO21
    const int SERVO1_PIN = 33;  // IO37
    const int SERVO2_PIN = 34;  // IO38
    const int SERVO3_PIN = 7;   // IO3
    const int SERVO4_PIN = 13;  // IO9
    const int LDR1_PIN = 9;   // IO5
    const int LDR2_PIN = 11;  // IO7
    const int LDR3_PIN = 10;  // IO6
    const int LDR4_PIN = 17;  // IO13
    const int LDR5_PIN = 8;   // IO4
#else
    // Dev Board Configuration
    #define DEV_BOARD
    const int LED1_PIN = 2;  // Just use built-in LED
    // Other pins undefined
#endif

// Network configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL = "http://192.168.43.243:8080/api/devices/checkin";

// Device configuration
#ifdef PROTO2_BOARD
    const char* FIRMWARE_VERSION = "1.0.0-proto2";
#else
    const char* FIRMWARE_VERSION = "1.1.1-dev";
#endif

const int CHECK_IN_INTERVAL = 30000; // 30 seconds
unsigned long lastCheckin = 0;

// GUID storage
Preferences preferences;
String deviceGuid = "";

void setup() {
    Serial.begin(115200);
    
    // Initialize pins based on board type
    #ifdef PROTO2_BOARD
        // Full Proto 2 initialization
        pinMode(LED1_PIN, OUTPUT);
        pinMode(LED2_PIN, OUTPUT);
        pinMode(LED3_PIN, OUTPUT);
        pinMode(LED4_PIN, OUTPUT);
        pinMode(LED5_PIN, OUTPUT);
        pinMode(LASER1_PIN, OUTPUT);
        pinMode(LASER2_PIN, OUTPUT);
        pinMode(LDR1_PIN, INPUT);
        pinMode(LDR2_PIN, INPUT);
        pinMode(LDR3_PIN, INPUT);
        pinMode(LDR4_PIN, INPUT);
        pinMode(LDR5_PIN, INPUT);
    #else
        // Dev board - just built-in LED
        pinMode(LED1_PIN, OUTPUT);
    #endif

    // Get stored GUID
    preferences.begin("laser-maze", false);
    deviceGuid = preferences.getString("guid", "");
    Serial.print("Stored GUID: ");
    Serial.println(deviceGuid);

    // Connect to WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConnected to WiFi");
    Serial.print("IP: ");
    Serial.println(WiFi.localIP());

    // Initial check-in
    performCheckin();
}

void loop() {
    if (millis() - lastCheckin >= CHECK_IN_INTERVAL) {
        performCheckin();
    }

    // Basic LED blink to show we're alive
    #ifdef DEV_BOARD
        static unsigned long lastBlink = 0;
        if (millis() - lastBlink >= 1000) {
            static bool ledState = false;
            digitalWrite(LED1_PIN, ledState);
            ledState = !ledState;
            lastBlink = millis();
        }
    #endif
}

void performCheckin() {
    if (WiFi.status() != WL_CONNECTED) {
        LOG_LN("WiFi not connected. Skipping check-in.");
        return;
    }

    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");

    // Prepare JSON payload
    StaticJsonDocument<1024> doc;
    doc["guid"] = deviceGuid;
    doc["firmware_version"] = FIRMWARE_VERSION;
    doc["ip_address"] = WiFi.localIP().toString();

    JsonArray capabilities = doc.createNestedArray("capabilities");

    #ifdef PROTO2_BOARD
        // Full Proto 2 capabilities
        capabilities.add("LED1");
        capabilities.add("LED2");
        capabilities.add("LED3");
        capabilities.add("LED4");
        capabilities.add("LED5");
        capabilities.add("LASER1");
        capabilities.add("LASER2");
        capabilities.add("LDR1");
        capabilities.add("LDR2");
        capabilities.add("LDR3");
        capabilities.add("LDR4");
        capabilities.add("LDR5");
        capabilities.add("SERVO1");
        capabilities.add("SERVO2");
        capabilities.add("SERVO3");
        capabilities.add("SERVO4");
    #else
        capabilities.add("LED1");
        capabilities.add("DEV_BOARD");
    #endif

    String payload;
    serializeJson(doc, payload);
    LOG("Sending payload: ");
    LOG_LN(payload);

    int httpCode = http.POST(payload);
    if (httpCode > 0) {
        String response = http.getString();
        LOG("Server response: ");
        LOG_LN(response);

        StaticJsonDocument<200> responseDoc;
        DeserializationError error = deserializeJson(responseDoc, response);

        if (!error && responseDoc.containsKey("guid")) {
            if (deviceGuid.length() == 0) {
                deviceGuid = responseDoc["guid"].as<String>();
                preferences.putString("guid", deviceGuid);
                LOG("Stored new GUID: ");
                LOG_LN(deviceGuid);
            }
        }
    } else {
        LOG("Check-in failed: ");
        LOG_LN(http.errorToString(httpCode));
    }

    http.end();
    lastCheckin = millis();
}