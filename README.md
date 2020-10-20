# paper-portraits
Photo frame with a display, camera, and raspberry pi.

### Setup
Install some basics
```bash
sudo apt-get install git python3.7 vim
```

Then clone the repository locally and CD into it.
```bash
git clone ...repo url from github...
cd paper-portraits
```

Decent chance it breaks midway through. If that happen, see where it crashed in `setup.sh` and finish the setup from there.
```bash
sudo ./setup.sh
```

### Running

Run from the repository folder.
```bash
sudo python3 app.py 
```
With debug printing.
```bash
sudo python3 app.py --debug
```

With debug printing and no display which is significantly faster.
```bash
sudo python3 app.py --debug --no_display
```

With GCP storage (requires a GCP identity and correctly named bucket).
```bash
sudo python3 app.py --google_cloud_identity_filepath /home/pi/paper-portraits/keys/my_key.json
```
