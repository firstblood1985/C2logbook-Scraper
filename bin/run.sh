#!/bin/bash

alias python=python3.8
source env/bin/activate

python ./MyC2Scraper.py -c ./MyC2Config.json

python ./load_data.py -c ./MyC2Config.json
