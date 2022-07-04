#!/bin/bash

set -eu

pip install -r requirements.txt
pylint_runner && echo "Looking good!"
