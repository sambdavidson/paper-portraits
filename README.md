# paper-portraits
Photo frame with a display, camera, and raspberry pi.

### Setup
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

With GCP storage (requires a GCP identity and correctly named bucket).
```bash
sudo python3 app.py --google_cloud_identity_filepath /home/pi/paper-portraits/keys/my_key.json
```
