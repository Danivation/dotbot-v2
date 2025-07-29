#!/bin/bash

cd /home/daniel/Documents/dotbot/

# Get commit hash before pulling
before=$(git rev-parse HEAD)

# Pull updates
git pull

# Get commit hash after pulling
after=$(git rev-parse HEAD)

# Check if screen is already running
if screen -list | grep -q "dotbot"; then
  screen_running=true
else
  screen_running=false
fi

# Restart screen if updated or not running
if [ "$before" != "$after" ] || [ "$screen_running" = false ]; then
  echo "Update detected or screen not running. Restarting bot..."

  # Kill existing screen if it's running
  if [ "$screen_running" = true ]; then
    echo "Killing existing screen session..."
    screen -S dotbot -X quit
  fi

  # Start the bot in a new screen
  echo "Starting new screen session..."
  screen -dmS dotbot bash -c '
    cd /home/daniel/Documents/dotbot/
    source venv/bin/activate
    python3 bot.py
  '
else
  echo "No update and bot already running — nothing changed."
fi
