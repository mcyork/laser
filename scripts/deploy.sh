#!/bin/bash
# Script to deploy to Raspberry Pi
TARGET_HOST="laser.local"  # Pi's mDNS hostname
TARGET_DIR="/opt/laser_maze"

# Push to git first if needed
# git push origin main

# SSH into Pi and pull changes
ssh $TARGET_HOST "cd $TARGET_DIR && sudo -u laser_maze git pull && sudo systemctl restart laser_maze"
