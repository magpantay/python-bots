import sys
import time
import requests

def print0(text, times, isBeeping = 0):
	print text,
	for i in range(times):
		if isBeeping == 0:
			time.sleep(1)
		sys.stdout.write('.')
		sys.stdout.flush()
		if isBeeping == 1:
			sys.stdout.write("\a")
			sys.stdout.flush()
			time.sleep(1.25)
	print "done."

####################################################################################################
#### 	The following function is a "beta" feature that isn't quite fully working 		####
#### 	If anyone wants to get this working before I figure out how to do it, be my guest 	####
def parse_data(current_result):
	firstNameBeginIndex = current_result.find("firstName")
	dateCreatedBeginIndex = current_result.find("\",\"dateCreated")		

	parsed_data = current_result[firstNameBeginIndex:dateCreatedBeginIndex-len(current_result)] #creates substring, starts at firstNameBeginIndex, gets (negative number) dateCreated minus length of entire thing
	parsed_data = parsed_data.replace(",", "\n").replace("\"", "")
	
	return parsed_data
####################################################################################################

params = (
    ('minDate', 'TODAY'),
    ('maxDate', 'TODAY'),
    ('calendarID', '646552'),
)

string0 = set()			#prevents duplicates of the same request
first_time_running = 1			#acts slightly differently on first run-through

numberoftimes = raw_input("Times to play beep (default: 5): ")
if numberoftimes == "":
	numberoftimes = "5"			#default is 5
numberoftimes = int(numberoftimes)

while 1:
	something_new = 0
	response = requests.get('https://acuityscheduling.com/api/v1/appointments', params=params, auth=('[]', '[]'))
	current_result = response.text.replace("\\n", "\n").replace("\\","")			#must be response.text because reponse just prints the code (i.e., 200 OK or 403 FORBIDDEN, etc.)
	
	string0_size_old = len(string0)
	string0.add(current_result)
	
	if len(string0) > string0_size_old:
		something_new = 1

	#new_file = open("acuity_appointments_metadata.txt", "w+")
	#new_file.write(current_result)			#Notepad is a dumb and won't display the new file correctly, use another text editor that isn't trash

	if first_time_running == 0:
		print0("Running", 3)

		if something_new == 1:
			time.sleep(1)
			print "\nThere's a new appointment."
			time.sleep(0.5)
			print0("Playing beep", numberoftimes, 1)
			time.sleep(0.3)
			print "\n=================\n"

		else:
			time.sleep(1)
			print "\nNothing new."
			time.sleep(0.3)
			print "\n=================\n"
	
	else:
		print "==============================================================METADATA=============================================================="
		print "----------------------------------------------------------------------"
		print current_result
		print "----------------------------------------------------------------------"
		print "============================================================END METADATA============================================================\n"
		
		#print parse_data(current_result)
		#print ""

		first_time_running = 0
		print "First time running, will sleep for 5 seconds and check again.\n"
	
	print0("Sleeping", 5)

#to-do: account for array shrinkages in the case someone cancels an appointment
#to-do: be able to parse metadata for if there's more than one appointment
#curl -u []:[] "https://acuityscheduling.com/api/v1/appointments?minDate=TODAY&maxDate=TODAY&calendarID=646552"
