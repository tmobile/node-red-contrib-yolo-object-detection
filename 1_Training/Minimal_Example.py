import os
import subprocess
import time
import sys


# Get model type if specified.  Fallback to default if not specified.
YOLO_MODEL = os.getenv("YOLO_MODEL", "yolov3")

# Lower logging level.
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


def make_call_string(arglist):
    result_string = ""
    for arg in arglist:
        result_string += "".join(["--", arg[0], " ", arg[1], " "])
    return result_string


# Set up folder names for default values
root_folder = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(root_folder, "Data")
model_folder = os.path.join(data_folder, "Model_Weights")
image_folder = os.path.join(data_folder, "Source_Images")
input_folder = os.path.join(image_folder, "Test_Images")
output_folder = os.path.join(image_folder, "Test_Image_Detection_Results")
src_path = os.path.join("2_Training", "src")

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

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

''' TODO: disable for now until we have a standard custom model.
# First download the pre-trained weights
download_script = os.path.join(model_folder, "Download_Weights.py")

if not os.path.isfile(os.path.join(model_folder, "trained_weights_final.h5")):
    print("\n", "Downloading Pretrained Weights", "\n")
    start = time.time()
    call_string = " ".join(
        [
            "python",
            download_script,
            "1MGXAP_XD_w4OExPP10UHsejWrMww8Tu7",
            os.path.join(model_folder, "trained_weights_final.h5"),
        ]
    )

    subprocess.call(call_string, shell=True)

    end = time.time()
    print("Downloaded Pretrained Weights in {0:.1f} seconds".format(end - start), "\n")
'''

# Now run the detector
detector_script = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "3_Inference", "Detector.py"
)


result_file = os.path.join(output_folder, "Detection_Results.csv")
anchors = os.path.join(
    root_folder, "2_Training", "src", "keras_yolo3", "model_data", "yolo_anchors.txt"
)

arglist = [
    ["input_path", input_folder],
    ["classes", classes_path],
    ["output", output_folder],
    ["yolo_model", model_weights],
    ["box_file", result_file],
    ["anchors", anchors_path],
    ["file_types", ".jpg .jpeg .png .mp4"],
]
call_string = " ".join(["python", detector_script, make_call_string(arglist)])

print("Detecting objects by calling: \n\n", call_string, "\n")
start = time.time()
subprocess.call(call_string, shell=True)
end = time.time()
print("Detected objects in {0:.1f} seconds".format(end - start))
