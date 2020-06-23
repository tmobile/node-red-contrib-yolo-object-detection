---
title: Notes
---

# Notes

This document captures further notes from researching and implementing
the solution.

TODO:  Add more detail as necessary.


## Model Options

Various model architectures and implementations are available that
typically tradeoff between speed and accuracy.  Smaller models typically
give up accuracy for the sake of less computation, memory, and speed.

The [TensorFlow Model Zoo](https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md) provides a sutie of prebuilt models rated by speed and accuracy.


## TensorFlow.js

The [TensorFlow.js](https://www.tensorflow.org/js) library allows models to be run purely within
JavaScript.  TensorFlow models have to be converted to the tfjs format
using provided tooling.

- Pros
  - Pure Node.js/JavaScript runtime at inference and not having to run Python
    TensorFlow separately if running in a JavaScript or Node.js
    environment such as Node-RED.
- Cons
  - Added step of having to convert Python TensorFlow model to TensorFlow.js.
  - Possible performance overhead running on Node.js/JavaScript.

Custom training would still be based on Python TensorFlow either way.
Further info on conversion provided [here](https://www.tensorflow.org/js/guide/conversion).

Some prebuilt models are provided [here](https://github.com/tensorflow/tfjs-models).


## Training Issues

Training accurate models for production accuracy can be challenging.
Some issues to consider.

- Training Data
  - Having enough good data to train with to cover your target inference
    domain is critical.
  - Challenge is having to annotate custom data manually and the effort
    involved.
- Instability
  - Models can exhibit instability when processing images and videos.
    You can typically see this in demonstrations of video and imagex
    object detection where objects detected come in and out.
  - In the case of YOLO, instability discussed here in the research paper [Large-Scale Object Detection of Images from Network Cameras in Variable Ambient Lighting Conditions](https://arxiv.org/pdf/1812.11901.pdf).
    - Excerpt:

```
The experiment uses 180 images taken every second from
3 network cameras and compares YOLO’s results with
ground truth. Figure 4 shows two images from these three
cameras. If an object is detected by YOLO, the bounding
box is shown. From this figure, it is clear that object
detection is unstable—some objects are detected in one
frame and missed in the next frame. Figure 5 compares
the numbers of objects detected by YOLO with that by
humans. This figure shows that in many cases YOLO’s
results are unstable. For example, in the New York alley, the
number of cars stayed at 2 during the 13th and 34th seconds
but YOLO’s reported only one car occasionally. As another
example, at the Streetside Cafe, during the 22nd and the
34th seconds, the number of people remained one. YOLO
detected 0, 1, and 2 in this duration. Overall, YOLO is
unstable at detecting objects in images one second apart on
the same camera. It is worth noting that YOLO’s accuracy
also strayed from the numbers reported in section III.A for
images taken an hour apart, further emphasizing YOLO’s
instability.
```

- Data Augmentation
  - Various methods are available to take a data set and add variance to
    improve accuracy.  For example shifting, rotating, translating
    images as part of the training process can potentially result in
    better model performance.
- Quantization
  - Quantization can be used to reduce computation and improve speed
    sacrificing potential accuracy by using techniques such as integers rather than
    floating point weights in the model.
  - Discussed further with TensorFlow [here](https://www.tensorflow.org/lite/performance/post_training_quantization).


## Inference Issues

Various things can affect model performance at runtime inference
including:

- Image Resolution
  - Higher resolution images will typically provide better detail for
    the model to run accurately against put add extra computation being larger.
- Lighting
  - Best to use proper lighting to ensure that the image provides detail
    used to train the model.
- Object Size, Proximity, and Occlusion
  - Models can have difficulty dealing with objects that are closer
    together or occluded/overlapping each other.

