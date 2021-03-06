# sahara_emulator

QC Sahara emulator
------------------------------------

Emulates QC Sahara using Raspberry Pi W Zero in order
to decrypt sahara loaders without mobile hardware :)

* Based on NCCGroup umap2: https://github.com/nccgroup/umap2

* initgadget.sh : Initialize GadgetFS in order to emulate USB device
* start.sh  : Start emulation
* dev/sahara.py : QC Sahara emulation implementation

Tested using python 3.6 and Raspberry Pi W Zero


Installation:
-------------
* You will need to set up Raspberry Pi W Zero image (kernel higher or equal 4.12.0-rc3+) and either wifi or uart connection
* See setup instructions over here for Raspberry Pi W Zero : https://learn.adafruit.com/turning-your-raspberry-pi-zero-into-a-usb-gadget/overview
* Example image ready for testing available at: https://revskills.de/usbemulator.zip

Usage:
------
* First start "initgadget.sh" once
* Set up device parameters in dev/sahara.py
* Then run "start.sh" to emulate your personal QDLoader 9008 device :D

License:
-------- 
Share, modify and use as you like, but refer to the original author !