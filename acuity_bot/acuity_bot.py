from platform import uname as os_id	#platform.uname()
from time import sleep 			#time.sleep()
from requests import get as web_get 	#requests.get()
from json import loads as json_parser 	#json.loads()
from sys import stdout as sysout 	#sys.stdout()

def doesExist(search_term, config_contents): # checks if an option ini file value exists and gets that value
	ret_0 = ""
	ret_1 = 0

	if config_contents.find(search_term) != -1:
		ret_0 = config_contents.split(search_term)[1]
		ret_0 = ret_0.split("'")[0]
		if ret_0 != "":
			ret_1 = 1
		else:
			print "WARNING: {0} value present in 'acuitybotconfig.ini' file, but is set to nothing.".format(search_term.split("='")[0])
	return [ret_0, ret_1]

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
		sysout.write('') # needed to print text first while waiting for "- done" in Linux, doesn't really do anything in Windows
		sysout.flush()	 # same as above
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
	calendarID_set = 0

	# ---- check OS (since some Linux distros has a different audio handling method) ---- #
	print "OS Detected as {0} {1}".format(os_id()[0], os_id()[2])

	# The following enables the beep sound for linux
	if os_id()[0].find("Linux") != -1 and os_id()[2].find("Microsoft") == -1: # is running non-Windows OS/non-Windows Linux
		print "NOTICE: Non-Windows/Ubuntu-Windows OS detected. Sudo access may be requested for the audio alerts to work [hopefully] properly."
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
	keyAPI = config_file_contents.split("keyAPI='")[1]		# meanwhile, the 1st index gets stuff after split
	userID = userID.split("'")[0]					# then remove the quotation mark on the other end for userID and API key
	keyAPI = keyAPI.split("'")[0]

	# -- check if optional ini values exist in file -- #
	calendarID_info = doesExist("calendarID='", config_file_contents)
	calendarID = calendarID_info[0]
	calendarID_set = calendarID_info[1]		# even if calendarID_info[0] is value "" (default not found value), calendarID_set will still be false
	del calendarID_info
	
	numTimes_info = doesExist("numberOfTimes='", config_file_contents)
	numberOfTimes = numTimes_info[0]
	numTimes_already_set = numTimes_info[1]		# even if numTimes_info[0] is value "" (default not found value), numTimes_already_set will still be false
	del numTimes_info		# no need for it anymore, just taking up space
	
	pullOnce_info = doesExist("pullOnce='", config_file_contents)
	if pullOnce_info[1]:		# if 1, we know that it's not blank
		if pullOnce_info[0] == 'Y' or pullOnce_info[0] == 'y':		# checks first return value for Y/y
			pullOnce = 1
	del pullOnce_info		# no need for it anymore, just taking up space
	# no need for an else statement because pullOnce is by default set to false
	# -- end optional ini value checking -- #

	del config_file_contents	# no need for it anymore, just taking up space

	if not numTimes_already_set:	# if optional line isn't in ini file
		numberOfTimes = raw_input("Times to play beep (default: 5): ")
		if numberOfTimes == "":
			numberOfTimes = "5"			#default is 5, put in quotes because it needs to be converted regardless (since raw_input)
		numberOfTimes = int(numberOfTimes)

	if not calendarID_set:
		print "WARNING: Calendar ID is not set. Please select an ID from the following list: "
		calendarID_list = web_get('https://acuityscheduling.com/api/v1/calendars', auth=(userID, keyAPI))

		if calendarID_list.status_code != 200: # < 200 OK >
			print "ERROR: Non-OK return status ({0}). Exiting...".format(response)
			exit()

		calendarID_list = json_parser(calendarID_list.text)

		# below you'll see that some things are offset by 1. I wanted to start at 1 as simple as possible (but it involved offsetting everything else)
		for i in range(len(calendarID_list)):
			print "{0}: {1}".format(i+1, calendarID_list[i]["name"])

		calendarID = raw_input("Enter choice: ")
		if calendarID == "" or int(calendarID) > len(calendarID_list) or int(calendarID) < 1:
			print "ERROR: Did not enter a valid choice. Exiting..."
			exit()
		calendarID = int(calendarID_list[int(calendarID)-1]["id"])

	# ---- end file reading and parsing ---- #

	params = ( ('minDate', 'TODAY'), ('maxDate', 'TODAY'), ('calendarID', calendarID), ) # for get request
	
	print "\nCalendar ID: {0}\n".format(calendarID)	

	if pullOnce:
		print "\nNOTICE: Pull once enabled. Will only pull current appointments once, auto-refresh disabled."

		print "\nGetting data from Acuity",
		sysout.write('') # needed to print text first while waiting for "- done" in Linux, doesn't really do anything in Windows
		sysout.flush()	 # same as above

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
			sysout.write('') # needed to print text first while waiting for "- done" in Linux, doesn't really do anything in Windows
			sysout.flush()	 # same as above

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
