#!/bin/bash

echo "Setting up Paper Portraits."
if [ "$EUID" -ne 0 ]
  then echo "Please run as root."
  exit
fi

cat "Installing Python3 Pillow"
apt-get install python3-pillow -qq

cat "Installing Python3 gpiozero"
apt-get install python3-gpiozero -qq

cat "Installing Python3 Facial Recognition"

