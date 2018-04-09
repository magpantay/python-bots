import sys
import time
import requests
import json

# The following enables the beep sound for linux
if sys.platform == "linux" or sys.platform == "linux2":
	import os
	# Beep drivers are removed by default in some linux distros (eg. Ubuntu)
	# To temporarily enable for current session, (until reboot)
	os.system("sudo modprobe pcspkr")
	os.system("xset b 100") # Perhaps not necissary, mine was set to 40.
	os.system("pactl upload-sample /usr/share/sounds/ubuntu/notifications/Mallet.ogg bell.ogg") # default bing sound. You may choose another (see to-do)
	# now to make beep, simply run:
	# os.system("printf \a")

def print0(text, times, isBeeping = 0):
	print text,
	for i in range(times):
		if isBeeping == 0:
			time.sleep(1)
		sys.stdout.write('.')
		sys.stdout.flush()
		if isBeeping == 1:
			if sys.platform == "linux" or sys.platform == "linux2": # beep on linux
				os.system("printf \a")
			else: 													# beep on windows
				sys.stdout.write("\a")
				sys.stdout.flush()
			time.sleep(1.25)
	print "done."

def printJSON(parsed_json_result):
	count = 1
	print "============================================================BEGIN=============================================================\n"
	for each_result in parsed_json_result:
		print "--------------"
		print "CLIENT #{0}: ".format(count)
		print "Name: {0} {1}".format(each_result['firstName'], each_result['lastName'])
		print "Phone: {0}".format(each_result['phone'])
		print "Email: {0}".format(each_result['email'])
		print "Appointment Time: {0}-{1}".format(each_result['time'], each_result['endTime'])
		print "Type of Service: {0}".format(each_result['forms'][0]['name'])

		if each_result['forms'][0]['name'] == "Dorm Run Request":
			print "Dorm Location: {0} {1}".format(each_result['forms'][0]['values'][2]['value'], each_result['forms'][0]['values'][3]['value'])
			print "What's Broken in the Dorm: {0}".format(each_result['forms'][0]['values'][0]['value'])
			print "Problem Elaboration by User: {0}".format(each_result['forms'][0]['values'][1]['value'])

		print "Work Order/Reference Number: {0}".format(each_result['forms'][1]['values'][0]['value'])
		print "--------------"
		count+=1
	print "\n=============================================================END==============================================================\n"

first_time_running = 1			#acts slightly differently on first run-through
numTimes_already_set = 0

# the following gathers information from a user-supplied INI file
config_file = open("acuitybotconfig.ini")
config_file_contents = config_file.read()
config_file.close()

# first remove the preceding part and first single quotation mark
userID = config_file_contents.split("userID='")[1]		# the 0th index gets the stuff preceding the split
calendarID = config_file_contents.split("calendarID='")[1]	# meanwhile, the 1st index gets stuff after split
keyAPI = config_file_contents.split("keyAPI='")[1]

if config_file_contents.find("numberOfTimes='") != -1:
	numberOfTimes = config_file_contents.split("numberOfTimes='")[1]
	numTimes_already_set = 1

del config_file_contents	# no need for it anymore, just taking up space

# then remove the quotation mark on the other end
userID = userID.split("'")[0]
calendarID = calendarID.split("'")[0]
keyAPI = keyAPI.split("'")[0]

if numTimes_already_set:
	numberOfTimes = numberOfTimes.split("'")[0]
	numberOfTimes = int(numberOfTimes)

# now that we're done with that, onto the rest of the program

params = (
    ('minDate', 'TODAY'),
    ('maxDate', 'TODAY'),
    ('calendarID', calendarID),
)

if numTimes_already_set != 1:
	numberOfTimes = raw_input("Times to play beep (default: 5): ")
	if numberOfTimes == "":
		numberOfTimes = "5"			#default is 5
	numberOfTimes = int(numberOfTimes)

size_old = 0

while 1:
	something_new = 0
	appt_cancelled = 0

	response = requests.get('https://acuityscheduling.com/api/v1/appointments', params=params, auth=(userID, keyAPI))
	current_result = response.text	#must be response.text because reponse just prints the code (i.e., 200 OK or 403 FORBIDDEN, etc.)
	parsed_json_result = json.loads(current_result) # type dictionary

	if size_old < len(current_result) and not first_time_running: # something_new doesn't trip on first iterance
		something_new = 1

	if size_old > len(current_result) and not first_time_running:
		appt_cancelled = 1

	if not first_time_running:
		print0("Running", 3)

		if something_new:
			time.sleep(1)
			print "\nThere's a new appointment."
			time.sleep(0.5)
			printJSON(parsed_json_result)
			print0("Playing beep", numberOfTimes, 1)
			time.sleep(0.3)
			print "\n=================\n"
		elif appt_cancelled:	# need to account for whether an appointment has been cancelled (but it only plays half the amount of specified beeps)
			time.sleep(1)
			print "\nSomeone cancelled their appointment."
			time.sleep(0.5)
			printJSON(parsed_json_result)
			print0("Playing beep", numberOfTimes/2, 1)
			time.sleep(0.3)
			print "\n================\n"
		else:
			time.sleep(1)
			print "\nNothing new."
			time.sleep(0.3)
			print "\n=================\n"

	else:
		printJSON(parsed_json_result)
		first_time_running = 0
		print "First time running, will sleep for 5 seconds and check again.\n"

	print0("Sleeping", 5)
	size_old = len(current_result)
