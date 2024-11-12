import asyncio
from typing import Dict, Tuple
import numpy as np
import cv2
from fastapi import FastAPI, WebSocket, Response
from ultralytics import YOLO
import io

app = FastAPI()

# UDP configuration
UDP_PORT = 5005
MAX_UDP_PACKET_SIZE = 65507  # Maximum size of a UDP packet

# YOLOv8 model
model = YOLO("best.pt")
# model.to('cuda')

# Image buffer to hold UDP data
image_buffer: Dict[str, bytes] = {}
# Memory buffer for the processed image
processed_image_data: bytes = None

class MyUDPProtocol(asyncio.DatagramProtocol):
    def connection_made(self, transport: asyncio.DatagramTransport) -> None:
        self.transport = transport

    def datagram_received(self, data: bytes, addr: Tuple[str, int]) -> None:
        # Store incoming UDP packets in the image buffer
        if addr[0] not in image_buffer:
            image_buffer[addr[0]] = data
        else:
            image_buffer[addr[0]] += data

        # Process the image after receiving enough data (assuming it's a complete image)
        if len(image_buffer[addr[0]]) > MAX_UDP_PACKET_SIZE:
            asyncio.create_task(self.process_image(addr))

    async def process_image(self, addr: Tuple[str, int]) -> None:
        global processed_image_data  # Use a global variable for in-memory storage

        # Get the raw image data from the buffer
        raw_image = image_buffer.pop(addr[0], None)
        if raw_image is None:
            return

        # Convert raw bytes to image (assuming JPEG format)
        np_img = np.frombuffer(raw_image, np.uint8)
        image = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        if image is None:
            return

        # Encode the image to JPEG and store it in memory
        _, processed_img = cv2.imencode('.jpg', image)
        processed_image_data = processed_img.tobytes()

# WebSocket endpoint to stream images to the frontend
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send the processed image if available
            if processed_image_data:
                await websocket.send_bytes(processed_image_data)
            await asyncio.sleep(0.05)  # Adjust the sleep time to control the frame rate
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

# Start the UDP server when the FastAPI server starts
@app.on_event("startup")
async def on_startup() -> None:
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: MyUDPProtocol(), local_addr=("0.0.0.0", UDP_PORT)
    )
    app.state.udp_transport = transport
    app.state.udp_protocol = protocol

# Close the UDP server when FastAPI server shuts down
@app.on_event("shutdown")
async def on_shutdown() -> None:
    app.state.udp_transport.close()

# Serve the HTML page
@app.get("/", response_class=Response)
async def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Live Video Stream</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
            }
            img {
                width: 50%;
                height: auto;
                margin: 20px auto;
                display: block;
                border: 1px solid #ccc;
            }
        </style>
    </head>
    <body>
        <h1>Live Object Detection Stream</h1>
        <img id="imageStream" alt="Live Stream" />
        <script>
            var imgElement = document.getElementById('imageStream');
            var ws = new WebSocket("ws://" + window.location.host + "/ws");

            ws.binaryType = 'blob';  // Receive binary data (images) as blobs

            ws.onmessage = function(event) {
                var blob = event.data;
                var objectURL = URL.createObjectURL(blob);
                imgElement.src = objectURL;
                imgElement.onload = function() {
                    URL.revokeObjectURL(objectURL);  // Free memory once the image is loaded
                };
            };

            ws.onclose = function(event) {
                console.log('WebSocket closed.');
            };
        </script>
    </body>
    </html>
    """
    return Response(content=html_content, media_type="text/html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.1.25", port=8000)
