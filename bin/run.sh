#!/bin/bash

python ./MyC2Scraper.py -c ./MyC2Config.json

python ./load_data.py -c ./MyC2Config.json
