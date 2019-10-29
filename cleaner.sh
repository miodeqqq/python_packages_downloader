#!/bin/sh
clear; find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf
rm -rf .DS_Store