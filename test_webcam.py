import cv2
from ultralytics import YOLO

# Load your YOLOv8 model
model = YOLO('best.pt')

# Open webcam (0 is the default webcam index, change if needed)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Set the webcam resolution if needed
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2480)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

while True:
    # Read frame from the webcam
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to read frame from webcam.")
        break

    # Perform detection
    results = model(frame, verbose=False)

    # Visualize the results on the frame
    annotated_frame = results[0].plot()

    # Display the annotated frame
    cv2.imshow('YOLOv8 Action Detection', annotated_frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close the display window
cap.release()
cv2.destroyAllWindows()
