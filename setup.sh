#!/bin/bash

printf "Setting up Paper Portraits."
if [ "$EUID" -ne 0 ]
  then printf "Please run as root."
  exit
fi

printf "PAPER PORTRAITS SETUP"
printf "This script hypothetically gets everything working on a fresh Raspberry Pi Zero"
printf "I created this script as I was manually performing all the actions over SSH."
printf "I haven't actually run this script start to finish with a fresh Pi."
printf "It might break and you will have to manually finish the job."
read -p "Press enter to acknowledge that the script sucks but you're gonna try anyways..."

printf "Updating apt-get:\n"
apt-get update -qq
apt-get upgrade -qq

printf "Installing Python3 pillow:\n"
apt-get install -qq python3-pillow

printf "Installing Python3 gpiozero:\n"
apt-get install -qq python3-gpiozero

printf "Installing Python3 picamera:\n"
apt-get install -qq python3-picamera
# Maybe run after facial stuff: sudo pip3 install --upgrade picamera[array]

printf "Installing Python3 Facial Recognition:\n"
printf "\tInstalling essential apt packages:\n"
apt-get install -qq build-essential \
    cmake \
    gfortran \
    python3 \
    vim \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-base-dev \
    libavcodec-dev \
    libavformat-dev \
    libboost-all-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    python3-pip \
    zip
apt-get clean

printf "\tEnable temporary larger swap file:\n"
sed -i 's/CONF_SWAPSIZE=100/CONF_SWAPSIZE=1028/g' /etc/dphys-swapfile
/etc/init.d/dphys-swapfile restart

printf "\tDownloading dlib:\n"
mkdir -p dlib
git clone -b 'v19.6' --single-branch https://github.com/davisking/dlib.git dlib/

printf "\tBuilding dlib:\n"
cd ./dlib
python3 setup.py install --compiler-flags "-mfpu=neon"
cd ..

printf "\tInstalling face_recognition pip3 package:\n"
pip3 install face_recognition

printf "\tDisabling temporary larger swap file:\n"
sed -i 's/CONF_SWAPSIZE=1028/CONF_SWAPSIZE=100/g' /etc/dphys-swapfile
/etc/init.d/dphys-swapfile restart

printf "Installing Waveshare E-Paper:\n"
printf "\tInstalling WiringPi:\n"
mkdir -p wiringpi
cd ./wiringpi
wget https://www.waveshare.com/w/upload/f/f3/WiringPi.tar.gz
tar -xvzf WiringPi.tar.gz
cd ./wiringPi
chmod 777 build
./build
cd ../..

printf "\tInstalling C Library bcm2835:\n"
mkdir -p bcm2835
cd ./bcm2835
wget https://www.waveshare.com/w/upload/d/d8/Bcm2835-1.45.tar.gz
tar -xvzf Bcm2835-1.45.tar.gz
cd ./bcm2835-1.45
./configure
make
make check
make install
cd ../..

printf "\tInstalling Python Libraries:\n"
# Python RPi.GPIO
mkdir -p rpigpio
cd ./rpigpio
wget https://files.pythonhosted.org/packages/af/2f/407b6e4cc8a0bdf434825a160bba1807991886b63cce16a5f1a6e1f24cdf/RPi.GPIO-0.6.5.tar.gz
tar -xvzf RPi.GPIO-0.6.5.tar.gz
cd ./RPi.GPIO-0.6.5
sudo python3 setup.py install
cd ../..

apt-get -qq install python3-smbus
apt-get -qq install python3-serial

# Python spidev
mkdir -p spidev
cd ./spidev
wget https://files.pythonhosted.org/packages/36/83/73748b6e1819b57d8e1df8090200195cdae33aaa22a49a91ded16785eedd/spidev-3.2.tar.gz
tar -xvzf spidev-3.2.tar.gz
cd ./spidev-3.2
sudo python3 setup.py install

apt-get -qq install python3-imaging

printf "Configuring Raspiberry Pi Interfaces:\n"
printf "\n\n\nEntering raspi-config, do the following:"
printf "5. Interfacing Options -> P5 I2C -> Enable"
printf "^ Don't forget or screw that up!"
read -p "Press enter when ready..."
raspi-config

printf "\n\n\nEnsure both 'i2c-bcm2708' and 'i2c-dev' exist in /etc/modules"
printf "Maybe write this down so you don't forget when in vim."
read -p "Press enter when ready..."
sudo vim /etc/modules

printf "\n\n\nEntering raspi-config, do the following:"
printf "5. Interfacing Options -> P6 Serial -> Enable"
printf "^ Don't forget or screw that up!"
read -p "Press enter when ready..."
raspi-config

printf "\n\n\nEntering raspi-config, do the following:"
printf "5. Interfacing Options -> P4 SPI -> Enable"
printf "^ Don't forget or screw that up!"
read -p "Press enter when ready..."
raspi-config

printf "Installing Python3 google-cloud-storage:\n"
pip3 install --upgrade google-cloud-storage

printf "Installing assorted other things..."
apt-get install -qq libatlas-base-dev

