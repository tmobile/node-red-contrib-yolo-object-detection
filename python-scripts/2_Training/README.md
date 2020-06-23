---
title: Inventory Tracker Training
---

# Inventory Tracker: Training


## Training

Using the training images located in [`inventory/Data/Source_Images/Training_Images`](/Data/Source_Images/Training_Images) and the annotation file [`data_train.txt`](/Data/Source_Images/Training_Images/vott-csv-export) which we have created in the [previous step](/1_Image_Annotation/) we are now ready to train our YOLOv3 detector.

Here are some things to keep in mind when doing training.

- If you're not seeing expected accuracy with your trained model, you
  may need more varied quality training images representing your target domain.
- If you're planning on training on lots of images, you may want to look at GPU capable
  systems to improve training speed either available through local PC hardware or
  available through cloud services.

If training is too slow on your local machine, consider using cloud computing services such as AWS to speed things up. To learn more about training on AWS navigate to [`inventory/2_Training/AWS`](/2_Training/AWS).


## (Optional) Setup TensorFlow GPU

If your system has an Nvidia GPU, you should be able to install
Python TensorFlow GPU support to improve training performance
typically by 10x.  Go here for detailed instructions about installation
([TensorFlow GPU Installation](https://www.tensorflow.org/install/gpu)).
In particular NVIDIA GPU drivers, CUDA Toolkit, and cuDNN need to be
installed along with the TensorFlow.
For this solution, we're still using TensorFlow 1.x (rather than 2.x),
so be sure to follow the instructions for 1.x.  Be sure to uninstall the
prior non-GPU TensorFlow if installed as follows before perfoming the
steps provided by the link.

```
pip uninstall tensorflow
```

Once complete, to check whether Python is making use of your GPU, run the following
within Python.  The check should respond with true if the GPU is
working within TensorFlow.

```
python
>>> import tensorflow as tf
>>> tf.test.is_gpu_available()
True
```


## Download and Convert Pre-Trained Weights

Before getting started download the pre-trained YOLOv3 weights and convert them to the keras format. For now, we have included the pre-trained weights for convenience as part of the repo, so this step may not be necessary. To run both steps run the download and conversion script from within the [`inventory/2_Training`](/2_Training/) directory:

```
python Download_and_Convert_YOLO_weights.py
```

To list available command line options run `python Download_and_Convert_YOLO_weights.py -h`.

The weights are pre-trained on the [ImageNet 1000 dataset](http://image-net.org/challenges/LSVRC/2015/index) and thus work well for object detection tasks that are very similar to the types of images and objects in the ImageNet 1000 dataset.


## Train YOLOv3 Detector

To start the training, run the training script from within the [`inventory/2_Training`](/2_Training/) directory:

```
python Train_YOLO.py
```

Depending on your set-up, this process can take a few minutes to a few hours. The final weights are saved in [`inventory/Data/Model_weights`](/Data/Model_weights). To list available command line options run `python Train_YOLO.py -h`.



### That's all for training!

Next, go to [`inventory/3_Inference`](/3_Inference) to test your YOLO detector on new images!
