#!/bin/bash

# Update package list and install required dependencies for Chromium
apt-get update && apt-get install -y \
    libx11-xcb1 \
    libxcomposite1 \
    libxrandr2 \
    libxi6 \
    libxtst6 \
    libnss3 \
    libasound2 \
    libxcursor1 \
    libxdamage1 \
    libxshmfence1 \
    libgbm1 \
    libgtk-3-0 \
    libcurl4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    fonts-liberation \
    wget \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*