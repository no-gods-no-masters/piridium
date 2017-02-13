![Piridium](assets/logo-pridium-1000x225.png)

A Python-based Iridium communication library.

## Overview
### Reinventing The Wheel
When we started working on our project, we intended to use a pre-existing Python library ([MakerSnake's pyRockBlock](https://github.com/MakerSnake/pyRockBlock)) but soon realized we would require additional functionality. Two features missing from pyRockBlock are SDB Ring Alert detection, and the ability to store incoming messages in a non-volatile queue -- we also like tinkering with software, so writing a new open source Python library for RockBLOCK seemed like a fun challenge. [iridiumPy](https://github.com/johngrantuk/iridiumPy) was also investigated, but we decided developing our own library was easier than adapting that one to our needs.

Our library was written to be modular and easy to integrate into other projects. Contributions and additional usage examples are welcome.

### Functionality & Target Hardware
This Python library allows for two-way communication using a [RockBLOCK](http://www.rock7.com/products-rockblock) and the [Iridium](https://www.iridium.com/) satellite system. It facilitates the development of an application that relies on monitoring the serial port for ring requests, and provides a parser for displaying or otherwise processing and replying to the incoming data.

Our target hardware was a [Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/) running [Raspbian](https://www.raspberrypi.org/downloads/raspbian/), while additional testing was done on macOS and Ubuntu. We expect this application to run on other configurations ([Arduino](https://www.arduino.cc/), [C.H.I.P.](https://getchip.com/), etc.) but for the sake of this document, we'll refer to Raspberry Pi as the target hardware. Feedback on other working configurations would be appreciated.

Security is handled via simple auth over an HTTPS connection.

### Directory Structure
```
./
  config-example.ini : Configuration variables
  send_command.py    : Sends a command to the modem
    example/
      config-example.ini : Example application - configuration variables
      mt_receive.py      : Example application - receive MT data
      mt_respond.py      : Example application - respond to MT data
      mt_send.py         : Example application - send MT data
      mo_send.py         : Example application - send MO data
    modules/
      config.py : Simple ConfigParser wrapper
      logger.py : Logging setup
      modem.py  : Modem communication functions
      parse.py  : Handles incoming and outgoing requests
      queue.py  : Non-volatile disk-based message queue
```

## Software

### Dependencies
- Python 2.7.x
  - Required modules:
    - ConfigParser, getpass, optparse, os, re, serial, signal, sys, threading, time, urllib, urllib2, uuid
- Git (optional)
- Raspbian (untested with other \*nix flavors)

### Installation & Configuration
Installing the application is straightforward whether you're downloading a ZIP or cloning directly.

#### Via Download
- Download a copy of this repo.
- Unzip into a user-accessible folder on your Raspberry Pi.
- Unzip into a user-accessible folder on a server you wish to send messages from.
- Copy `./config-example.ini` to `./config.ini`.

#### Via Git (recommended)
- Clone directly from this repo into a user-accessible folder on your Raspberry Pi.
- Clone directly from this repo to a server you wish to send messages from.
- Copy `./config-example.ini` to `./config.ini`.

#### config.ini

##### log
`log_filename` (str) [`app.log`]
Filename for the logger to output to.

`log_name` (str) [`app`]
Internal name for the logger to reference within the application.

##### modem
`baud` (int) [`19200`]
Baud rate to communicate with the port.

`port` (str) [`/dev/ttyUSB0`]
Port to communicate with.

##### Retreiving Config Data
A wrapper has been built for ConfigParser to simplify and normalize the retreival of config data.
The correct syntax is `Config.get("section")["key"]`, where \<section> is required and [key] is optional. If you do not specify a [key] the function will return a dictionary object for the specified \<section>.

## Hardware

### Dependencies
- RockBLOCK Mk2 ([via Rock7](https://www.rock7.com/shop-product-detail?productId=46]))
- Raspberry Pi 3 ([via Amazon](https://www.amazon.com/Raspberry-Pi-RASP-PI-3-Model-Motherboard/dp/B01CD5VC92))
- FTDI Interface ([via DigiKey](http://www.digikey.com/product-detail/en/DEV-09716/1568-1103-ND/5318745))
  - Serial cable (optional) ([via Adafruit](https://www.adafruit.com/products/70))

### Configuration
- Connect RockBLOCK to Raspberry Pi (either via a serial cable, or by soldering your own UART connections).
- Connect your antenna to the RockBLOCK if you purchased a version without the onboard patch antenna.
- Consult [Rock7's Development Guide](http://www.rock7.com/downloads/RockBLOCK-Developer-Guide-Mk2.pdf) for more details.

## Usage
See: `./example/README.md` ([Link](example/))

## Integrating Piridium
Creating your own application that utilizes Piridium is straightforward.

- Sign up for a Rock7 account and familiarize your self with their web interface.
  - Read the documentation.
  - All of it.
- Create a new repo for your application.
- Either initialize Piridium as a submodule (preferred) in a library folder, or copy the code into your library folder.
  - Import the modules in your Python script per your directory structure, and refer to our `./example` application documentation.
