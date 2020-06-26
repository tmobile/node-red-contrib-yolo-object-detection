# YOLO3 Object Detector

<!-- [![Travis (.com) branch](https://img.shields.io/travis/com/tmobile/node-red-contrib-array-iterator/master?style=flat-square)](https://travis-ci.com/tmobile/node-red-contrib-array-iterator) ![GitHub package.json version](https://img.shields.io/github/package-json/v/tmobile/node-red-contrib-array-iterator?style=flat-square) [![npm (scoped)](https://img.shields.io/npm/v/@tmus/node-red-contrib-array-iterator?style=flat-square)](https://www.npmjs.com/package/@tmus/node-red-contrib-array-iterator) -->

Given a raw image/frame input, this node will run YOLO3-based object detection
on the input and output a list of detected objects.

## Install

TODO need to publish

## Usage

Drag and Drop the "Yolo Object Detector" onto the canvas.

## Advanced Usage

This module starts a local Python model server on port 8888 (TODO - make this configurable)

## Testing changes locally

1. Clone this repo and CD to repo folder
2. Run `npm link`
3. CD to your local node-red modules folder (`.node-red` or similar)
4. `npm link node-red-contrib-yolo-object-detector`
