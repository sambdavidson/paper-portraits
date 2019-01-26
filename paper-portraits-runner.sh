#!/bin/sh

while true;
do
	sudo python3 /home/pi/paper-portraits/app.py --google_cloud_identity_filepath /home/pi/paper-portraits/keys/personal-website-207903-ec4296051ff8.json
	echo "Paper Portraits crashed with exit code $?. Restarting..." >> ~/crash_errors.txt
done
