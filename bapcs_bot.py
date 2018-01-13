import praw
import time
import datetime

def convert_epoch_to_date(sub_time):
	time0 = datetime.datetime.fromtimestamp(sub_time)

	# the following is used to convert from UTC to PST -8 (I guess the long way)

	month_sub_factor = 0
	day_sub_factor = 0
	year_sub_factor = 0
	hour_sub_factor = 8

	if time0.hour-hour_sub_factor < 0:
		day_sub_factor = 1
		hour_sub_factor = 8-24
	  if time0.day-day_sub_factor < 1:
			month_sub_factor = 1
			if month == 2 and year % 4 != 0:
				day_sub_factor = 1-28
			elif month == 2 and year % 4 == 0:
				day_sub_factor = 1-29
			elif month != 1 or month != 3 or month != 5 or month != 7 or month != 8 or month != 10 or month != 12:
				day_sub_factor = 1-30
			else:
				day_sub_factor = 1-31
			if time0.month-month_sub_factor < 1:
				month_sub_factor = 1-12
				year_sub_factor = 1

	# the following is used to convert from military-styled timing to AM/PM styled timing
	
	PM = 0 #boolean for if AM or PM
	if time0.hour-hour_sub_factor > 12:
		hour_sub_factor = hour_sub_factor+12 #subtracts 12, switches to PM
		PM = 1
		
	if PM:
		return "{0:02}-{1:02}-{2:02} at {3:02}:{4:02}:{5:02}PM PST".format(time0.month-month_sub_factor,time0.day-day_sub_factor,time0.year-year_sub_factor,time0.hour-hour_sub_factor,time0.minute,time0.second) # :02 prints minimum 2 digits
	else:
		return "{0:02}-{1:02}-{2:02} at {3:02}:{4:02}:{5:02}AM PST".format(time0.month-month_sub_factor,time0.day-day_sub_factor,time0.year-year_sub_factor,time0.hour-hour_sub_factor,time0.minute,time0.second) # :02 prints minimum 2 digits
#######
print "Location of Praw: {0}\n".format(praw.__path__)

bot = praw.Reddit(password='[]',username='[]', client_secret='[]', client_id='[]', user_agent='BAPCS Bot v1.0')
subreddit = bot.subreddit('buildapcsales') 

keywords = ['ddr4', 'ssd'] 

for submission in subreddit.stream.submissions():
	if submission.link_flair_text != "Expired" and submission.link_flair_text != "Out Of Stock" and submission.title.lower().find("built") == -1 and submission.title.lower().find("laptop") == -1: #built used for pre-built
	  for i in range(len(keywords)):
			if submission.title.lower().find(keywords[i]) != -1:
				print "Title: {0}\nURL: {1}\nTime: {2}\n".format(submission.title,submission.url,convert_epoch_to_date(submission.created))
				subject_content = "[FROM BOT] Found {0} You May Want From {1}!".format(keywords[i].upper(), subreddit.display_name)
				message_content = "Title: {0}\n\nURL: {1}\n\nTime: {2}\n\n".format(submission.title,submission.url,convert_epoch_to_date(submission.created))	
				bot.redditor('[]').message(subject_content, message_content)
				break #just in case someone is selling both keywords in the same posting (don't want duplicate messages)

