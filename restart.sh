#!/bin/bash

cd /home/daniel/Documents/dotbot/

# Pull updates
git pull

# Kill existing screen
echo "Killing existing screen session..."
screen -S dotbot -X quit

# Start the bot in a new screen
echo "Starting new screen session..."
screen -dmS dotbot bash -c '
  cd /home/daniel/Documents/dotbot/
  source venv/bin/activate
  python3 bot.py
'