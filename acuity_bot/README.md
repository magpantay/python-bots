# Acuity Bot
For when you don't want to keep refreshing Acuity Scheduling's website every 5 seconds (exaggerated) to check if there are new appointments set up.

## Features
- Auto-fetches schedule metadata from Acuity's website every ~10 seconds for the current day only
- Alerts the user whether either a new appointment is scheduled or an appointment cancelled

## Preinstallation Requirements
You need the following:
- python
    - (`sudo apt-get install python`)
- pip 
    - (`sudo apt-get install python-pip`)
- requests
    - (`sudo pip install requests`)


## Running Acuity Bot
- Fill out INI configuration file (acuitybotconfig.ini) with API key, the user ID, and the calendar ID you'd like to keep fetching
     - Note: All of these are user-specific. If you need help finding these, there is information on how to on [Acuity's website](https://developers.acuityscheduling.com/v1.1/reference#quick-start).
- Navigate to the folder where both the config file and the Python script are, and run command: `python acuity_bot.py`
    
