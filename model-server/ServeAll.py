#!/usr/bin/env python3

import base64
from gevent.pywsgi import WSGIServer
import io
import os
import signal
import sys
import shutil
from threading import Thread


def get_parent_dir(n=1):
    """ returns the n-th parent dicrectory of the current
    working directory """
    current_path = os.path.dirname(os.path.abspath(__file__))
    for k in range(n):
        current_path = os.path.dirname(current_path)
    return current_path


src_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(src_path)

# Get model path. Default to home directory models/yolov3.
MODEL_PATH = os.getenv("YOLO_MODEL_PATH",os.path.join(
    os.getenv("HOME"), "models", "yolov3"))

# Lower logging level.
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from utils import load_extractor_model, load_features, parse_input, detect_object
from keras_yolo3.yolo import YOLO, detect_video
from PIL import Image, ImageFont, ImageDraw

# Set related model file paths based on base path convention.
anchors_path = os.path.join(MODEL_PATH, "anchors.txt")
classes_path = os.path.join(MODEL_PATH, "classes.txt")
model_weights = os.path.join(MODEL_PATH, "weights.h5")

gpu_num = 1
model_image_size = (416, 416)
score = .25

from flask import Flask, json, jsonify, request
app = Flask(__name__)


def init_yolo(model_weights, anchors_path, score, gpu_num, model_image_size):
    yolo = YOLO(
        **{
            "model_path": model_weights,
            "anchors_path": anchors_path,
            "classes_path": classes_path,
            "score": score,
            "gpu_num": gpu_num,
            "model_image_size": model_image_size,
        }
    )
    print("MODELSERVER: Model initialized")
    return yolo


@app.route('/',methods=['POST','GET'])
def detect():
    global yolo
    # Get input image.
    # DBG print("is_json:", request.is_json)
    if request.is_json:
        content = request.get_json()
        image = Image.open("frame.jpg")
    else:
        content = request.data
        image = Image.open(io.BytesIO(content))
    # DBG image = Image.open("test.jpg")
    # Use local capture frame from video stream instead.
    if image.mode != "RGB":
        image = image.convert("RGB")

    # Perform object detection.
    detections, new_image = yolo.detect_image(image)

    # DBG Save image with bounding boxes from detection.
    # DBG new_image.save("result.jpg")
    image_buffer = io.BytesIO()
    new_image.save(image_buffer, format="JPEG")
    base64_image = base64.b64encode(image_buffer.getvalue()).decode("utf-8")

    # DBG print("detections", detections)
    result = {
            "image": base64_image,
            "detections": [],
            "things": []
            }
    # DBG print("yolo.class_names", yolo.class_names)
    # detection = (left, top, right, bottom, class, score).
    for detection in detections:
        # DBG print("detection:", detection)
        left = int(detection[0])
        top = int(detection[1])
        right = int(detection[2])
        bottom = int(detection[3])
        class_id = int(detection[4])
        class_name = yolo.class_names[class_id]
        score = float(detection[5])
        final_detection = {
            'bbox': [ left, top, right, bottom ],
            'class': class_name,
            'score': score
        }
        print("detection:", final_detection)
        result["detections"].append(final_detection)
        result["things"].append({"thing": class_name})

    # DBG print("result:", result)

    # return jsonify(result)
    response = app.response_class(
        response=json.dumps(result),
        status=200,
        mimetype='application/json'
    )
    return response


def sig_handler(signum, frame):
    print("Serve caught signal:", signum)
    print("Exiting...")
    os._exit(0)


def run_video_thread(srcpath, camera_mode):
    try:
        if not camera_mode or camera_mode == "picamera":
            print("Running ServeVideoPiCamera...")
            import ServeVideoPiCamera
    except:
        print("Caught camera exception from ServeVideoPiCamera.")
    finally:
        if not camera_mode or camera_mode == "opencv":
            print("Running ServeVideo...")
            import ServeVideo
            ServeVideo.main()


def run_video(camera_mode):
    dirpath = os.path.dirname(os.path.realpath(__file__))
    srcpath = dirpath + "/ServeVideo.py"
    video_thread = Thread(target = run_video_thread, args = (srcpath, camera_mode))
    video_thread.start()


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    run_video(os.getenv("CAMERA_MODE", ""))
    yolo = init_yolo(model_weights, anchors_path, score, gpu_num, model_image_size)
    http_server = WSGIServer(('', 8888), app)
    http_server.serve_forever()
