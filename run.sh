# Create looping camera photo
fswebcam -r 640x480 --no-banner -loop 3 --background --save sample/capture.jpg
# Create looping FBI process
fbi -T 2 -a -noverbose -t 3 -cachemem 0 sample/capture.jpg 
# Run python
echo "Run python"
