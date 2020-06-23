---
title: Inventory Tracker Serve
---

# Inventory Tracker: Serve

In this step, we serve our model via a Python Flask web services script.  This service
is used by the Node-RED flow to detect objects.  We also run a video streaming service
from the camera used by the Node-RED dashboard UI to display active
video.


## Serving Your Model

To serve your model using Flask from the [`inventory/4_Serve](/4_Serve/) directory:

```
# Run with default prebuilt YOLOv3 model in the background.
python Serve.py &

# Run with tiny prebuilt YOLOv3 model for speed, but less accuracy.
YOLO_MODEL=yolov3-tiny python Serve.py &
```

To start the live video streaming service in the background, execute the following.  On a
Raspberry Pi with Pi Camera module installed, execute the following:

```
python ServeVideoPiCamera.py &
```

For other setups making use of opencv enabled cameras, execute the following:

```
python ServeVideo.py &
```

The current implementation saves the latest frame as a JPEG image in the
current directory for the model serve script above to pick and process
for object detection as part of the Node-RED UI dashboard flow.
