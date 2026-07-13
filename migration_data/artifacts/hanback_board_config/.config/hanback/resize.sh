#!/bin/sh

sudo /usr/lib/nvidia/resizefs/nvresizefs.sh
sleep 3
sed -i 's|(sudo /home/soda/.config/hanback/resize.sh) &||' /home/soda/.config/openbox/autostart

