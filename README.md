# EvlDaemon [![Build Status](https://travis-ci.org/Tokenize/evl-daemon-python.png)](https://travis-ci.org/Tokenize/evl-daemon-python)

**A cross-plaform Python API and daemon for the Envisalink TPI (DSC) module**

**Requirements:** Python >= 3.5 and packages found in requirements.txt file.

**Note:** This version is a work in progress and may not be entirely stable and bug-free.
But it shouldn't melt your system, so there's that.

## Installation

1. Clone the repository: `git clone https://github.com/Tokenize/evl-daemon-python.git`
2. Install the requirements from requirements.txt: `pip install -r requirements.txt`

## Usage

1. Create a *config.json* file and save it to the directory of your choosing. You can use the config.json file as a
template. Ensure that the EVL IP, port number and password are specified.

2.  Run evldaemon: `python3 evldaemon.py --config=<config file path>`

## Configuration

See [config.json](config.json) for configuration for details.

## Coming up...

Some things planned for the future:

* SMS notifier via Twilio
* Email notifier via SendGrid
* Generic REST API notifier
* *And more!*
