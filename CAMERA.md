- Download Raspbian
- Put it on an SD card
- `touch /Volumes/boot/ssh`
- `ssh -X pi@IP`
- `passwd`
- (Optional) `mkdir .ssh && echo "PUB" >> ~/.ssh/authorized_keys`
- `sudo apt-get update`
- `sudo apt-get upgrade`
- `sudo modprobe bcm2835-v4l2`
