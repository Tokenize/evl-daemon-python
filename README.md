# EvlDaemon

A cross-platform Python API and daemon for the **Envisalink TPI (DSC)** module.

**Requirements:** Python >= 3.11 and [poetry](https://python-poetry.org).

## Installation

1. Clone the repository: `git clone https://github.com/Tokenize/evl-daemon-python.git`
2. Install the requirements using poetry: `poetry install`. If you don't want the development dependencies: `poetry install --no-dev`.

## Usage

1. Create a _config.json_ file and save it to the directory of your choosing. You can use the config.json file as a
   template. Ensure that the EVL IP, port number and password are specified.
2. Run evldaemon: `poetry run python3 evldaemon.py --config=<config file path>`

## Configuration

See [config.json](config.json) for configuration for details.

## Development

### Running tests

To run all unit tests, run the following:

```bash
poetry run python -m unittest discover test
```


