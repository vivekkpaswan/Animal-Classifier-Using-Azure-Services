#!/bin/bash

# Install Python dependencies
pip install Flask pillow torch torchvision azure-storage-blob requests

# Start Flask application in the background
python app.py &

# Start a simple HTTP server to serve the HTML file
python -m http.server 8000
