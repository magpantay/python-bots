from platform import uname as os_id	#platform.uname()
from time import sleep 			#time.sleep()
from requests import get as web_get 	#requests.get()
from json import loads as json_parser 	#json.loads()
from sys import stdout as sysout 	#sys.stdout()

def print0(text, times, isBeeping = 0):	# prints text, sleeps/makes sounds for amount of times
	print text,	# comma keeps text inline
	for i in range(times):
		if not isBeeping:
			sleep(1)
		else:
			if os_id()[0].find("Linux") != -1 and os_id()[2].find("Microsoft") == -1: # beep on linux
				system("printf \a")
			else: 									  # beep on windows
				sysout.write("\a")
				sysout.flush()
			sleep(1.25)
	print " - done."

def printJSON(parsed_json_result): # prints specific details of parsed JSON text
	count = 1 # used for the list numbering
	print "============================================================BEGIN=============================================================\n"
	for each_result in parsed_json_result:

		# Normal general print-out #
		print "--------------"
		print "CLIENT #{0}: ".format(count)
		print "Name: {0} {1}".format(each_result['firstName'], each_result['lastName'])
		print "Phone: {0}".format(each_result['phone'])
		print "Email: {0}".format(each_result['email'])
		print "Appointment Time: {0}-{1}".format(each_result['time'], each_result['endTime'])
		print "Type of Service: {0}".format(each_result['type'])
		print "Work Order/Reference Number: {0}".format(each_result['forms'][1]['values'][0]['value'])

		# ---- Location-specific printouts ---- #
		# On-Campus Travel Tech #
		if each_result['forms'][0]['name'].find("Campus Location") != -1:
			print ""
			print "{0}".format(each_result['forms'][0]['name'])
			print "Location: {0} {1}".format(each_result['forms'][0]['values'][0]['value'], each_result['forms'][0]['values'][1]['value']) #location + rm/ste value

		# Bobcat Bar (COB132A)/Non-dorm-run dorm locations#
		elif each_result['type'] == "Rufus (Campus) Tech Time" or each_result['type'] == "Rufus Tech - Housing":
			print "User explanation of problem: {0}".format(each_result['forms'][0]['values'][0]['value']) #different notes location for Student Rufus Time location
			print ""

		# Remote Tech #
		elif each_result['type'] == "Phone/Remote Support":
			print "{0}".format(each_result['location']) #supposedly where the zoom link is

		# GP/VT locations for dorm runs #
		elif each_result['forms'][0]['name'] == "Dorm Run Request":
			print "Dorm Location: {0} {1}".format(each_result['forms'][0]['values'][2]['value'], each_result['forms'][0]['values'][3]['value'])
			print "What's Broken in the Dorm: {0}".format(each_result['forms'][0]['values'][0]['value'])
			print "User explanation of problem: {0}".format(each_result['forms'][0]['values'][1]['value'])
			print ""
		# ---- End location-sepcific printouts ---- #

		print "Additional Appointment Notes: {0}".format(each_result['notes'])

		print "--------------"
		count+=1
	print "\n=============================================================END==============================================================\n"

def main():
	first_time_running = 1			#acts slightly differently on first run-through
	numTimes_already_set = 0		#to set default value if not set in ini file
	pullOnce = 0				#pulls all appointment information only once, doesn't do the automatic refresh thing

	# ---- check OS (since some Linux distros has a different audio handling method) ---- #
	print "OS Detected as {0} {1}".format(os_id()[0], os_id()[2])

	# The following enables the beep sound for linux
	if os_id()[0].find("Linux") != -1 and os_id()[2].find("Microsoft") == -1: # is running non-Windows OS/non-Windows Linux
		from os import system
		# Beep drivers are removed by default in some linux distros (eg. Ubuntu, but not Bash on Ubuntu on Windows)
		# To temporarily enable for current session, (until reboot)
		system("sudo modprobe pcspkr")
		system("xset b 100") # Perhaps not necessary, mine was set to 40.
		system("pactl upload-sample /usr/share/sounds/ubuntu/notifications/Mallet.ogg bell.ogg") # default bing sound. You may choose another (see to-do)
		# now to make beep, simply run:
		# system("printf \a")
	# ---- end check OS ---- #

	# ---- read and parse through file ---- #
	# the following gathers information from a user-supplied INI file
	config_file = open("acuitybotconfig.ini")
	config_file_contents = config_file.read()
	config_file.close()

	# first remove the preceding part and first single quotation mark
	userID = config_file_contents.split("userID='")[1]		# the 0th index gets the stuff preceding the split
	calendarID = config_file_contents.split("calendarID='")[1]	# meanwhile, the 1st index gets stuff after split
	keyAPI = config_file_contents.split("keyAPI='")[1]

	if config_file_contents.find("numberOfTimes='") != -1:	# if optional line found in ini file
		numberOfTimes = config_file_contents.split("numberOfTimes='")[1]
		numberOfTimes = numberOfTimes.split("'")[0]
		if numberOfTimes != "":
			numberOfTimes = int(numberOfTimes)
			numTimes_already_set = 1
		else:
			print "WARNING: numberOfTimes value is present in 'acuitybotconfig.ini' file, but is set to nothing."

	if config_file_contents.find("pullOnce='") != -1:	# if optional line found in ini file
		pullOnce = config_file_contents.split("pullOnce='")[1]
		pullOnce = pullOnce.split("'")[0]
		if pullOnce != "":
			if pullOnce == 'Y' or pullOnce == 'y':
				pullOnce = 1				# no need for else seeing as default is 0
			else:
				pullOnce = 0				# needed because pullOnce changed to Y/N in previous lines
		else:
			print "WARNING: pullOnce value is present in 'acuitybotconfig.ini' file, but is set to nothing. Setting default to false..."

	del config_file_contents	# no need for it anymore, just taking up space

	# then remove the quotation mark on the other end
	userID = userID.split("'")[0]
	calendarID = calendarID.split("'")[0]
	keyAPI = keyAPI.split("'")[0]
	
	if not numTimes_already_set:	# if optional line isn't in ini file
		numberOfTimes = raw_input("Times to play beep (default: 5): ")
		if numberOfTimes == "":
			numberOfTimes = "5"			#default is 5, put in quotes because it needs to be converted regardless (since raw_input)
		numberOfTimes = int(numberOfTimes)
	# ---- end file reading and parsing ---- #

	params = ( ('minDate', 'TODAY'), ('maxDate', 'TODAY'), ('calendarID', calendarID), ) # for get request
	
	print "Calendar ID: {0}\n".format(calendarID)	

	if pullOnce:
		print "\nNOTICE: Pull once enabled. Will only pull current appointments once, auto-refresh disabled."

		print "\nGetting data from Acuity",

		response = web_get('https://acuityscheduling.com/api/v1/appointments', params=params, auth=(userID, keyAPI))
		
		print " - done"

		if response.status_code != 200: # <200 OK>
			print "ERROR: Non-OK return status ({0}). Exiting...".format(response)
			exit()

		parsed_json_result = json_parser(response.text)	#must be response.text because reponse just prints the code (i.e., 200 OK or 403 FORBIDDEN, etc.), # type dictionary
		printJSON(parsed_json_result)

		print "Exiting..."
		exit()
	else:
		old_len = 0 # used to keep track of amount of appointments
		while 1:
			something_new = 0
			appt_cancelled = 0

			print "Getting data from Acuity", # commas keep text inline

			response = web_get('https://acuityscheduling.com/api/v1/appointments', params=params, auth=(userID, keyAPI))
			
			print " - done"
			
			if response.status_code != 200: # <200 OK>
				print "ERROR: Non-OK return status ({0}). Exiting...".format(response)
				exit()

			parsed_json_result = json_parser(response.text)	#must be response.text because reponse just prints the code (i.e., 200 OK or 403 FORBIDDEN, etc.), # type dictionary

			if len(parsed_json_result) > old_len and not first_time_running: # something_new doesn't trip on first iterance
				something_new = 1

			if old_len > len(parsed_json_result) and not first_time_running:
				appt_cancelled = 1

			if not first_time_running:
				if something_new:
					sleep(0.5)	# just a slight delay
					print "\nThere's a new appointment."
					printJSON(parsed_json_result)
					print0("Playing beep {0} times".format(numberOfTimes), numberOfTimes, 1)
					print "\n=================\n"
				elif appt_cancelled:	# need to account for whether an appointment has been cancelled (but it only plays half the amount of specified beeps)
					sleep(0.5)	# just a slight delay
					print "\nSomeone cancelled their appointment."
					printJSON(parsed_json_result)
					print0("Playing beep {0} times".format(numberOfTimes/2), numberOfTimes/2, 1)
					print "\n================\n"
				else:
					sleep(0.5)	# just a slight delay
					print "\nNothing new."
					print "\n=================\n"

			else:
				first_time_running = 0
				printJSON(parsed_json_result)

			print0("Sleeping for 5 seconds", 5) # this plus all the other delays means a refresh happens about every 5-10 seconds
			old_len = len(parsed_json_result)

if __name__ == "__main__":
	main()
	# really, this is meant for calendars that AREN'T Checked-in Troubleshooting and Device Pickup
