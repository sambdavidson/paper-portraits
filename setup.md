# Setup

## Python Facial Reconition

Github: https://github.com/ageitgey/face_recognition

Raspberry Pi Installation: https://gist.github.com/ageitgey/1ac8dbe8572f3f533df6269dab35df65

Also run:
```bash
sudo apt-get install libatlas-base-dev
```

Just follow those and then move on.

## Capture webcam image (command line tool)

Installation 
```bash
sudo apt-get install fswebcam
```

Run

```bash
fswebcam -r 1280x720 --no-banner capture.jpg
```

Run continuously in background
```bash
fswebcam -r 1280x720 --no-banner --loop 1 --background --pid sample/fswebcam_pid.txt sample/capture.jpg
```

## Display Images FBI

[Forum Post](https://www.raspberrypi-spy.co.uk/2017/02/how-to-display-images-on-raspbian-command-line-with-fbi/)

```bash
sudo apt-get update
sudo apt-get -y install fbi
```

Displaying over SSH

```bash
sudo fbi -T 2 img.png
```

