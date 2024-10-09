import cv2
import numpy as np
import urllib.request
from ultralytics import YOLO

# Set the URL for your ESP32-CAM feed
url = 'http://192.168.1.104/cam-hi.jpg'

# Load the trained YOLOv8 model (you can replace this with your custom model)
model = YOLO('best.pt')  # 'best.pt' is the YOLOv8 nano model, use the model you want

# Function to process and find objects using YOLOv8
def find_and_draw_objects(image):
    results = model(image, verbose=False)  # Run inference on the image
    boxes = results[0].boxes  # Get detected bounding boxes

    # Iterate over detected boxesz
    for box in boxes:
        # Extract bounding box coordinates
        x_min, y_min, x_max, y_max = map(int, box.xyxy[0])  # Convert to integer values
        confidence = box.conf[0]  # Confidence score
        class_id = int(box.cls[0])  # Class ID

        if confidence > 0.5:
            # Draw bounding box and label
            label = f'{model.names[class_id]}: {confidence:.2f}'  # Get the class name and confidence
            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            cv2.putText(image, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    return image

while True:
    try:
        # Capture the image from the ESP32-CAM URL
        img_resp = urllib.request.urlopen(url)
        imgnp = np.array(bytearray(img_resp.read()), dtype=np.uint8)
        im = cv2.imdecode(imgnp, -1)  # Decode image to OpenCV format

        # Run YOLOv8 to find and draw objects
        processed_image = find_and_draw_objects(im)

        # Display the processed image
        cv2.imshow('YOLOv8 Detection', processed_image)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except Exception as e:
        print(f"Error: {e}")

# Release the video capture and close windows
cv2.destroyAllWindows()
