# EvlDaemon ![Build and Test](https://github.com/tokenize/evl-daemon-python/actions/workflows/build-and-test.yml/badge.svg?branch=main) ![CodeQL](https://github.com/tokenize/evl-daemon-python/actions/workflows/codeql-analysis.yml/badge.svg?branch=main)

A cross-platform Python API and daemon for the **Envisalink TPI (DSC)** module.

**Requirements:** Python >= 3.11 and [uv](https://docs.astral.sh/uv/).

## Installation

1. Clone the repository: `git clone https://github.com/Tokenize/evl-daemon-python.git`
2. Install the requirements using poetry: `uv sync`. If you don't want the development dependencies: `uv sync --no-dev`.

## Usage

1. Create a _config.json_ file and save it to the directory of your choosing. You can use the included config.json file as a template. Ensure that the EVL IP, port number and password are specified.
2. Run evldaemon: `uv run ./evldaemon.py --config=<config file path>`

## Configuration

See [config.json](config.json) for configuration for details.

## Development

### Running tests

To run all unit tests, run the following:

```bash
uv run python -m unittest discover test
```
