#!/bin/bash

#wrap running the script inside a virtual X server
xvfb-run -s "-screen 0 1920x1080x16" -a python3 run_example1.py
