#include <WiFi.h>
#include <WiFiUdp.h>
#include "esp_camera.h"

const char* ssid = "IEC-Local";
const char* password = "IEC@2023";
// const char* ssid = "Interdimensional_Wifi";
// const char* password = "0974603489";

WiFiUDP udp;
const char* udp_server_ip = "192.168.1.25";  // IP address of the FastAPI server
const int udp_server_port = 5005;  // UDP port of the FastAPI server

#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27
#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("WiFi connected");
  
  udp.begin(udp_server_port);

  Serial.println("ESP32-CAM IP Address: ");
  Serial.println(WiFi.localIP());

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  if(psramFound()){
    config.frame_size = FRAMESIZE_HVGA;
    config.jpeg_quality = 16;
    config.fb_count = 1;
  } else {
    config.frame_size = FRAMESIZE_HVGA;
    config.jpeg_quality = 16;
    config.fb_count = 1;
  }

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    delay(500);
    ESP.restart();
  }

  WiFi.setTxPower(WIFI_POWER_19_5dBm);  // Set maximum WiFi transmission power
}

void loop() {
  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    delay(500);
    ESP.restart();
  }

  // Limit packet size to around 1024 bytes (MTU)
  const size_t packet_size = 1024;
  size_t len = fb->len;
  uint8_t *buf = fb->buf;
  
  for (size_t offset = 0; offset < len; offset += packet_size) {
    size_t chunk_size = (len - offset < packet_size) ? len - offset : packet_size;
    udp.beginPacket(udp_server_ip, udp_server_port);
    udp.write(buf + offset, chunk_size);
    udp.endPacket();
  }

  esp_camera_fb_return(fb);
  delay(3);
}