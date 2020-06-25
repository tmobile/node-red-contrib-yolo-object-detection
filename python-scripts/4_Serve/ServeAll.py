#!/usr/bin/env python3

import base64
from gevent.pywsgi import WSGIServer
import io
import os
import signal
import sys
import shutil


def get_parent_dir(n=1):
    """ returns the n-th parent dicrectory of the current
    working directory """
    current_path = os.path.dirname(os.path.abspath(__file__))
    for k in range(n):
        current_path = os.path.dirname(current_path)
    return current_path


src_path = os.path.join(get_parent_dir(1), "2_Training", "src")
utils_path = os.path.join(get_parent_dir(1), "Utils")

sys.path.append(src_path)
sys.path.append(utils_path)

# Get model type if specified.  Fallback to default if not specified.
YOLO_MODEL = os.getenv("YOLO_MODEL", "yolov3")

# Lower logging level.
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

from utils import load_extractor_model, load_features, parse_input, detect_object
from keras_yolo3.yolo import YOLO, detect_video
from PIL import Image, ImageFont, ImageDraw

# Set up folder names for default values
current_folder = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(get_parent_dir(n=1), "Data")
model_folder = os.path.join(data_folder, "Model_Weights")
image_folder = os.path.join(data_folder, "Source_Images")
image_test_folder = os.path.join(image_folder, "Test_Images")

# Custom trained model settings.
if YOLO_MODEL == "custom":
    anchors_path = os.path.join(src_path, "keras_yolo3", "model_data", "yolo_anchors.txt")
    classes_path = os.path.join(model_folder, "data_classes.txt")
    model_weights = os.path.join(model_folder, "trained_weights_final.h5")
# Custom trained model settings.
elif YOLO_MODEL == "custom-tiny":
    anchors_path = os.path.join(src_path, "keras_yolo3", "model_data", "yolo-tiny_anchors.txt")
    classes_path = os.path.join(model_folder, "data_classes.txt")
    model_weights = os.path.join(model_folder, "trained_weights_final_tiny.h5")
# Prebuilt model settings.
elif YOLO_MODEL == "yolov3":
    anchors_path = os.path.join(src_path, "keras_yolo3", "model_data", "yolo_anchors.txt")
    classes_path = os.path.join(src_path, "keras_yolo3", "model_data", "coco_classes.txt")
    model_weights = os.path.join(src_path, "keras_yolo3", "yolo.h5")
# Tiny model settings.
elif YOLO_MODEL == "yolov3-tiny":
    anchors_path = os.path.join(src_path, "keras_yolo3", "model_data", "yolo-tiny_anchors.txt")
    classes_path = os.path.join(src_path, "keras_yolo3", "model_data", "coco_classes.txt")
    model_weights = os.path.join(src_path, "keras_yolo3", "yolov3-tiny.h5")

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
    print("Model ready...")
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
        class_name = yolo.class_names[class_id],
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
    print("Caught signal: ", signum)
    print("Exiting...")
    exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGTERM, sig_handler)
    signal.signal(signal.SIGINT, sig_handler)
    yolo = init_yolo(model_weights, anchors_path, score, gpu_num, model_image_size)
    # app.run(host='0.0.0.0', debug=False, port=8888, threaded=False)
    http_server = WSGIServer(('', 8888), app)
    http_server.serve_forever()
