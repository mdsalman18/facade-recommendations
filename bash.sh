#!/bin/bash

# Install system dependencies (for building C extensions)
apt-get update
apt-get install -y gcc g++ libomp-dev ninja

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
