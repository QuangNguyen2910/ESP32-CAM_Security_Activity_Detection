import asyncio
from typing import Dict
import numpy as np
import cv2
from fastapi import FastAPI, Response
from ultralytics import YOLO
import requests
import os

app = FastAPI()

# YOLOv8 model
model = YOLO("best.pt")

# ESP32-CAM URL (replace with your actual ESP32 IP)
ESP32_CAM_URL = "http://192.168.0.19/cam-hi.jpg"  # Replace with your ESP32-CAM IP

# Location where the processed image will be saved
ANNOTATED_IMAGE_PATH = "annotated_image.jpg"

# Fetch and process the image from ESP32-CAM
async def fetch_and_process_image():
    try:
        # Fetch image from ESP32-CAM over HTTP
        response = requests.get(ESP32_CAM_URL)
        if response.status_code == 200:
            # Convert raw bytes to image
            np_img = np.frombuffer(response.content, np.uint8)
            image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

            # Perform object detection using YOLOv8
            results = model(image)
            annotated_image = results[0].plot()

            # Save the annotated image locally
            cv2.imwrite(ANNOTATED_IMAGE_PATH, annotated_image)
        else:
            print(f"Failed to fetch image from ESP32-CAM, status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching or processing image: {str(e)}")


# HTTP route to serve the latest processed image
@app.get("/processed_image")
async def get_processed_image():
    # Fetch and process image asynchronously
    await fetch_and_process_image()

    # Check if the processed image file exists
    if os.path.exists(ANNOTATED_IMAGE_PATH):
        with open(ANNOTATED_IMAGE_PATH, "rb") as image_file:
            return Response(content=image_file.read(), media_type="image/jpeg")
    return {"error": "No image available"}


# Serve the HTML page
@app.get("/", response_class=Response)
async def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Security Camera Stream - Trusted Tech</title>
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap" rel="stylesheet">
        <style>
            body { font-family: 'Roboto', sans-serif; background-color: #f4f4f9; margin: 0; padding: 0; display: flex; flex-direction: column; align-items: center; justify-content: space-between; height: 100%; }
            header { background-color: #4CAF50; color: white; padding: 10px; width: 100%; text-align: center; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2); margin-bottom: 10px; }
            header h1 { margin: 0; font-size: 2.5em; font-weight: 700; }
            header p { margin: 0; font-size: 1.2em; font-weight: 300; }
            .container { display: flex; flex-direction: column; align-items: center; width: 80%; max-width: 600px; background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1); }
            .live-stream { position: relative; background-color: #000; width: 100%; max-width: 640px; height: 480px; border-radius: 10px; overflow: hidden; }
            .live-stream img { width: 640px; height: 480px; }
            footer { margin-top: 10px; font-size: 0.9em; color: #888; }
            footer p { margin: 0; }
        </style>
    </head>
    <body>
        <header>
            <h1>Security Camera Dashboard</h1>
            <p>Your trusted surveillance solution</p>
        </header>
        <div class="container">
            <div class="live-stream">
                <img id="liveStream" src="/processed_image" alt="Live Stream">
            </div>
        </div>
        <footer>
            <p>&copy; 2024 TrustedTech Security Solutions. All rights reserved.</p>
        </footer>
        <script>
            const liveStream = document.getElementById('liveStream');

            // Function to refresh the live stream image every 20 milliseconds
            function refreshImage() {
                liveStream.src = '/processed_image?time=' + new Date().getTime();  // Prevent caching
            }

            // Start refreshing the image stream
            setInterval(refreshImage, 20);
        </script>
    </body>
    </html>
    """
    return Response(content=html_content, media_type="text/html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.0.2", port=8001)
