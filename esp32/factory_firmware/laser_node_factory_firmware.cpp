#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <Preferences.h>

// Network configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL = "http://192.168.43.243:8080/api/devices/checkin";

// Device configuration
const char* FIRMWARE_VERSION = "1.0.0";
const int CHECK_IN_INTERVAL = 30000; // 30 seconds
unsigned long lastCheckin = 0;

// GUID storage
Preferences preferences;
String deviceGuid = "";

// LED pins (for Proto 1)
const int LED_PINS[] = {
    LED_BUILTIN,  // Built-in LED
    // Add your actual LED pins here
};
const int NUM_LEDS = sizeof(LED_PINS) / sizeof(LED_PINS[0]);

void setup() {
    Serial.begin(115200);
    
    // Initialize LEDs
    for (int i = 0; i < NUM_LEDS; i++) {
        pinMode(LED_PINS[i], OUTPUT);
    }

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
    // Other loop functionality here
}

void performCheckin() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi not connected. Skipping check-in.");
        return;
    }

    HTTPClient http;
    http.begin(SERVER_URL);
    http.addHeader("Content-Type", "application/json");

    // Create capabilities array
    StaticJsonDocument<200> capabilities;
    JsonArray array = capabilities.to<JsonArray>();
    for (int i = 0; i < NUM_LEDS; i++) {
        array.add(String("LED") + (i + 1));
    }

    // Create check-in payload
    StaticJsonDocument<512> doc;
    if (deviceGuid.length() > 0) {
        doc["guid"] = deviceGuid;
    }
    doc["firmware_version"] = FIRMWARE_VERSION;
    doc["capabilities"] = capabilities;
    doc["ip_address"] = WiFi.localIP().toString();

    String payload;
    serializeJson(doc, payload);
    Serial.print("Sending payload: ");
    Serial.println(payload);

    int httpCode = http.POST(payload);
    if (httpCode > 0) {
        String response = http.getString();
        Serial.print("Server response: ");
        Serial.println(response);

        // Parse response
        StaticJsonDocument<200> responseDoc;
        DeserializationError error = deserializeJson(responseDoc, response);
        
        if (!error) {
            // If this was our first check-in and we got a GUID, store it
            if (deviceGuid.length() == 0 && responseDoc.containsKey("guid")) {
                deviceGuid = responseDoc["guid"].as<String>();
                preferences.putString("guid", deviceGuid);
                Serial.print("Stored new GUID: ");
                Serial.println(deviceGuid);
            }
        }
    } else {
        Serial.print("Check-in failed: ");
        Serial.println(http.errorToString(httpCode));
    }

    http.end();
    lastCheckin = millis();
}