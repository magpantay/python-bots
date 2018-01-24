import sys
import time
import requests

params = (
    ('minDate', 'TODAY'),
    ('maxDate', 'TODAY'),
    ('calendarID', '646552'),
)

string0 = set()
first_time_running = 1

numberoftimes = raw_input("Times to play beep: ")
numberoftimes = int(numberoftimes)
while 1:
	something_new = 0
	response = requests.get('https://acuityscheduling.com/api/v1/appointments', params=params, auth=('[]', '[]'))
	current_result = response.text.replace("\\n", "\n").replace("\\","") # must be response.text because reponse just prints the code (i.e., 200 OK or 403 FORBIDDEN, etc.)
	string0_size_old = len(string0)
	string0.add(current_result)
	if len(string0) > string0_size_old:
		something_new = 1
	
  #new_file = open("acuity_appointments_halfdome_fixed.txt", "w+")
	#new_file.write(current_result) #Notepad is a dumb and won't display the new file correctly, use another text editor that isn't trash

	if first_time_running == 0:
		print "Running",
		for i in range(0,3):
			time.sleep(1)
			sys.stdout.write('.')
			sys.stdout.flush()
		print "done."
		if something_new == 1:
			time.sleep(1)
			print "\nThere's a new appointment."
			time.sleep(0.5)
			print "Playing beep",
			for i in range(numberoftimes):
				sys.stdout.write('.')
				sys.stdout.flush()
				sys.stdout.write("\a")
				sys.stdout.flush()
				time.sleep(1.25)
			time.sleep(0.3)
			print "\n\n=================\n"
		else:
			time.sleep(1)
			print "\nNothing new."
			time.sleep(0.3)
			print "\n=================\n"
	else:
		first_time_running = 0
		print "First time running, will sleep for 5 seconds and check again.\n"

	print "Sleeping",
	for i in range(0,5):
		time.sleep(1)
		sys.stdout.write('.')
		sys.stdout.flush() # the premier way of printing stuff in python without newlines being involved
	print "done."

#to-do: account for array shrinkages in the case someone cancels an appointment
#curl -u []:[] "https://acuityscheduling.com/api/v1/appointments?minDate=TODAY&maxDate=TODAY&calendarID=646552" -o acuity_appointments_halfdome_raw.txt
