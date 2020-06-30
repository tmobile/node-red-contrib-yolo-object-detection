#!/usr/bin/env python3
# Serve MJPEG stream using picamera interface.

import io
import os
import picamera
import logging
import socketserver
from threading import Condition
from PIL import ImageFont, ImageDraw, Image
import cv2
import traceback
# from io import StringIO
from io import BytesIO

import numpy as np

import datetime as dt

#import SimpleHTTPServer

from http.server import BaseHTTPRequestHandler,HTTPServer

PAGE="""\
<html>
<head>
<title>IoT-Mobile Video Stream</title>
</head>
<body>
<h1>IoT-Mobile Video Stream</h1>
<img src="stream.mjpg" width="320" height="240" />
</body>
</html>
"""

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                        # now add timestamp to jpeg
                        # Convert to PIL Image
                        cv2.CV_LOAD_IMAGE_COLOR = 1 # set flag to 1 to give colour image
                        npframe = np.frombuffer(frame, dtype=np.uint8)
                        pil_frame = cv2.imdecode(npframe,cv2.CV_LOAD_IMAGE_COLOR)
                        #pil_frame = cv2.imdecode(frame,-1)
                        cv2_im_rgb = cv2.cvtColor(pil_frame, cv2.COLOR_BGR2RGB)
                        pil_im = Image.fromarray(cv2_im_rgb)

                        draw = ImageDraw.Draw(pil_im)

                        # Save the image
                        buf= BytesIO()
                        pil_im.save(buf, format= 'JPEG')
                        # Save latest frame to filesytem.
                        pil_im.save("frame-buffer.jpg", format= 'JPEG')
                        # Buffer frame until fully saved.
                        os.rename("frame-buffer.jpg", "frame.jpg")
                        frame = buf.getvalue()
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                traceback.print_exc()
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

#with picamera.PiCamera(resolution='1920x1080', framerate=24) as camera:
#with picamera.PiCamera(resolution='320x240', framerate=24) as camera:
with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    camera.annotate_foreground = picamera.Color(y=0.2,u=0, v=0)
    camera.annotate_background = picamera.Color(y=0.8, u=0, v=0)
    try:
        address = ('', 22334)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()

