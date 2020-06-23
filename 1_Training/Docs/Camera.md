---
title: Inventory Tracker Camera Support
---

# Camera Support

Here are some things to keep in mind when dealing with cameras and
object detection.

- Focus
  - The Raspberry Pi Camera Module has a manually focused lens that may
    need to be adjusted based on your .
    - Depending on the version you've purchased, the focus may be adjusted
      from the factory for nearby or far away objects as detailed [here](https://www.jeffgeerling.com/blog/2017/fixing-blurry-focus-on-some-raspberry-pi-camera-v2-models).
    - Latest version 2.1 comes with the focus set for infinity (far)
      from the factory.
    - It comes with a [plastic lens adjustment tool](https://www.adafruit.com/product/3518)
      to attach to the lens to manually adjust the focus.
        - Adjust the focus (clockwise for far focus, counter-clockwise for
      near focus).
- Lighting
  - Typically the better the lighting provided for a camera, the better
    your machine learning model will be able to detect objects.
  - You may be able to set the camera for a longer exposure to deal with
    this but you'll sacrificing speed and get mixed results.
  - If considering low light conditions, you may want to consider
    cameras supporting low light conditions and/or training images in
    low light situations.
- Exposure
  - Cameras may have different exposure settings and capabilities for
    dealing with exposure and other things like saturation, brightness,
    contrast, sharpness, etc. that may need to be adjusted and
    specified.
  - Camera software tools typically provide different options for
    adjusting these settings.
