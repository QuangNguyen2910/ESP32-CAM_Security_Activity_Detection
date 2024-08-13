### ESP32-CAM Object Detection with YOLO and Voice Output

Watch this video

https://github.com/user-attachments/assets/396b6a6d-eac9-43d1-b17e-61e40c0b4a01

This project demonstrates the integration of an ESP32-CAM module with a Python script to perform real-time object detection using the YOLO model. The detected objects are also announced using a text-to-speech engine. The project is split into two main components:

1. **ESP32-CAM Setup (Arduino Code)**
   - The Arduino code sets up the ESP32-CAM module to capture images at different resolutions. The images are served over a local network via a simple web server running on the ESP32.
   - The web server provides three endpoints for capturing images at low, medium, and high resolutions.

2. **Object Detection and Voice Output (Python Code)**
   - The Python script captures the image feed from the ESP32-CAM, processes it using the YOLOv3-tiny model to detect objects, and provides real-time feedback by drawing bounding boxes around the detected objects.
   - The script also includes a text-to-speech feature that announces the name of the object detected with the highest confidence.

### Features:
- **Real-time Object Detection**: Leverages the YOLOv3-tiny model for efficient and accurate object detection.
- **Text-to-Speech Announcement**: The Python script uses the `pyttsx3` library to audibly announce the detected object with the highest confidence.
- **ESP32-CAM Web Server**: The ESP32-CAM is configured as a web server to stream images in low, medium, and high resolutions, selectable through different endpoints.

### Requirements:
- **Hardware**: ESP32-CAM module.
- **Software**: 
  - Python with `opencv-python`, `numpy`, and `pyttsx3` libraries.
  - Arduino IDE for uploading the ESP32-CAM code.
  - YOLOv3-tiny weights and configuration files.

### How to Use:
1. Upload the Arduino code to your ESP32-CAM module to set up the web server.
2. Run the Python script to start the object detection process.
3. Access the image feed from the ESP32-CAM, and the script will detect objects and announce them in real-time.

### Future Enhancements:
- Adding support for multiple objects' voice output.
- Integrating video streaming for continuous detection.

This project showcases the seamless integration of an ESP32-CAM module with a Python script for real-time object detection and voice output. The combination of hardware and software components demonstrates the power of edge computing and IoT applications.

---