# Inventory Tracker: Track Items with Object Detection

Developer documentation provided below.

## Raspberry Pi Setup

Make sure you are starting with the standard [kit](../../kit/) image on your [Raspberry Pi](../../kit/raspberry-pi/).

> NOTE: You may also find it convenient to connect the `~/.node-red` folder on the Pi to the [node-red-config](../../node-red-config) Git repository to make collaborating on configuration changes easy - you can do this by configuring Github authentication locally on your Pi, or by editing remotely over SSH using the remote editing functionality of Visual Studio Code and other editors, or simply by copying the folder to your local machine and diffing it when you're done developing on the Pi.

## Windows Setup

Windows installation info [IoT-Mobile Kit Windows](../../../kit/windows).

## Quick Start

```
# Clone this repo.
cd ~/.node-red/projects
git clone git@gitlab.com:tmobile/iot-mobile/projects/inventory.git
```

Next, open a web browser (e.g. Chrome) to your Node-RED instance. If you are running Node-RED locally with the default port,
use <http://localhost:1880>.

> Note: This document assumes you are running Node-RED locally. If running a Raspberry Pi on your network with its default hostname of
raspberrypi.local, you can access it at <http://raspberrypi.local:1880>.

Now that you have access to the Node-RED interface, you can open the Inventory project by going to the Main Menu ➡ `Projects` ➡ `inventory`.

To use the inventory flow, refer to the top level [README](../README.md).

## Acknowledgements

Many thanks to [Anton Mu](https://github.com/AntonMu) for his [TrainYourOwnYOLO](https://github.com/AntonMu/TrainYourOwnYOLO) repo serving a template and starting point for this repo and also to the [IBM team](https://github.com/IBM) for their example [node-red-tensorflowjs](https://github.com/IBM/node-red-tensorflowjs) repo.

