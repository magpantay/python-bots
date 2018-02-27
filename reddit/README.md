# Reddit Bots
For helping you look through Reddit so you don't need to keep mashing that refresh button

## Current Reddit Bots
- [r/buildapcsales](https://www.reddit.com/r/buildapcsales) bot
- [r/hardwareswap](https://www.reddit.com/r/hardwareswap) bot

(Technically, these are two bots that have super similar purposes, and were consolidated into one Python file)

## Preinstallation Requirements
You need the following to run the r/buildapcsales and r/hardwareswap bot:
- python
  - `sudo apt-get install python`
- pip
  - `sudo apt-get install python-pip`
- praw
  - `sudo pip install praw`

## Running the Python Scripts
### r/hardwareswap and/or r/buildapcsales bot
- Fill out the corresponding INI file for the bot you are trying to run (or both if you want to run both)
- Open the Python script and change the value "is_hws" to a 0 (false) to run the r/buildapcsales bot and a 1 (true) to run the r/hardwareswap bot
- Ensure the INI file(s) are in the same directory as the Python script(s), and run the Python script(s)

Note: If you want to run both, you need to have two copies of the same file, one with the "is_hws" boolean value set to 0 and the other one with the "is_hws" boolean value set to 1
