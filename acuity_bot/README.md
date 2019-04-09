# Acuity Bot
For when you don't want to keep refreshing Acuity Scheduling's website every few seconds to check if there are new appointments set up/existing appointments cancelled.

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

## INI Config File
The INI file is a configuration file that is required for the program to run.
- userID: The login information given in the [Acuity website](https://developers.acuityscheduling.com/v1.1/reference#quick-start). Note: This is NOT the same as your Acuity login username/e-mail.
- keyAPI: The secret API key (basically a password) given in the [Acuity website](https://developers.acuityscheduling.com/v1.1/reference#quick-start). Note: This is NOT the same as your Acuity login password.
- calendarID: The ID of the calendar that you are trying to fetch off of Acuity. Note: This is an optional value, the program will print a list of all calendars and prompt user to select a calendar from list if this value is missing.
- numberOfTimes: A numerical value that tells the program the amount of times you want a sound to play upon a new appointment being fetched. Note: This is an optional value, the program will prompt you in the case this line is missing/will default to a value of 5. Also, the amount of times the sound is played is halved (rounded down) in the case of an appointment cancellation to try to differentiate between the different appointment changes.
- pullOnce: A Y/N value that tells the program whether to run once or not. If Y, the program will only fetch the appointments once then exit. Note: This is an optional value, the program will default to the the value N in the case that this value is missing.

## Running Acuity Bot
- Fill out INI configuration file (acuitybotconfig.ini) with API key, the user ID, and the calendar ID you'd like to keep fetching
     - Note: All of these are user-specific. If you need help finding these, there is information on how to on [Acuity's website](https://developers.acuityscheduling.com/v1.1/reference#quick-start).
- Navigate to the folder where both the config file and the Python script are, and run command: `python acuity_bot.py`
    
