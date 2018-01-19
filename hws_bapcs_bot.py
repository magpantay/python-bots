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

def print_and_send_post(username, bot, subreddit, submission, found_keyword, hws_yes):
        if hws_yes:
            print "Flair: {0}\nTitle: {1}\nAuthor: /u/{2}\nURL: {3}\nTime: {4}\n".format(submission.link_flair_text,submission.title,submission.author,submission.url, convert_epoch_to_date(submission.created))
            subject_content = "[FROM BOT] Found {0} You May Want From {1}!".format(found_keyword.upper(), subreddit.display_name)
            message_content = "Flair: {0}\n\nTitle: {1}\n\nAuthor: /u/{2}\n\nURL: {3}\n\nTime: {4}\n\n".format(submission.link_flair_text,submission.title,submission.author,submission.url, convert_epoch_to_date(submission.created))	
            bot.redditor(username).message(subject_content, message_content)
        else: #bapcs_format
            print "Title: {0}\nURL: {1}\nTime: {2}\n".format(submission.title,submission.url,convert_epoch_to_date(submission.created))
            subject_content = "[FROM BOT] Found {0} You May Want From {1}!".format(found_keyword.upper(), subreddit.display_name)
            message_content = "Title: {0}\n\nURL: {1}\n\nTime: {2}\n\n".format(submission.title,submission.url,convert_epoch_to_date(submission.created))	
            bot.redditor(username).message(subject_content, message_content)

def check_locality(locality_country, locality_state, submission_title):
    return ((submission_title.lower().find("local") != -1 and submission_title.lower().find("paypal") == -1) and (submission_title.find(locality_country+"-"+locality_state) != -1 or submission_title.find(locality_country+" - "+locality_state) != -1)) or (submission_title.lower().find("paypal") != -1 and submission_title.find(locality_country))
    #finds "Local", doesn't find "Paypal", but in locality --OR-- it just finds "paypal" and is within country	   

def flair_check(submission, hws_yes):
    if hws_yes:
        return submission.link_flair_text == "Selling" or submission.link_flair_text == "None" #including "None" in the case it catches possible selling item that isn't marked yet
    else:
        return submission.link_flair_text != "Out of Stock" or submission.link_flair_text != "Expired"

###################

print "Location of Praw: {0}\n".format(praw.__path__)

is_hws = 1 #a switch whether this is the hws_bot or the bapcs_bot
if is_hws:
    bot = praw.Reddit(password='[]',username='[]', client_secret='[]', client_id='[]', user_agent='HWS/BAPCS Bot v2.0 [Mode: HWS]')
else:
    bot = praw.Reddit(password='[]',username='[]', client_secret='[]', client_id='[]', user_agent='HWS/BAPCS Bot v2.0 [Mode: BAPCS]')

if is_hws:
    subreddit = bot.subreddit('hardwareswap') 
else:
    subreddit = bot.subreddit('buildapcsales')

keywordsHWS = ['ddr4', 'ssd'] 
antikeywordsHWS = ['HTPC'] # may have the keywords above, but if there are any antikeywords in the title, then just ignore it despite the keyword match

keywordsBAPCS = ['ddr4', 'ssd']
antikeywordsBAPCS = ['built', 'laptop', 'build']

for submission in subreddit.stream.submissions():
    ignore_post = 0
    if flair_check(submission, is_hws): 
	if is_hws: #because checking locality is an hws_bot specific thing
            if check_locality('USA', 'CA', submission.title) != 1: #if the locality check fails
                continue #ignore this one
            for i in range(len(keywordsHWS)):
                if submission.title.lower().find(keywordsHWS[i]) != -1:
                    for j in range(len(antikeywordsHWS)):
                        if submission.title.lower().find(antikeywordsHWS[j]) != -1:
                            ignore_post = 1
                            break #we only need one ignore
                    if ignore_post != 1:
                        print_and_send_post('[]', bot, subreddit, submission, keywordsHWS[i], is_hws)
                        break #just in case someone is selling both keywords in the same posting (don't want duplicate messages)
        else:
            for i in range(len(keywordsBAPCS)):
                if submission.title.lower().find(keywordsBAPCS[i]) != -1:
                    for j in range(len(antikeywordsBAPCS)):
                        if submission.title.lower().find(antikeywordsBAPCS[j]) != -1:
                            ignore_post = 1
                            break #we only need one ignore
                    if ignore_post != 1:
                        print_and_send_post('[]', bot, subreddit, submission, keywordsBAPCS[i], is_hws)
                        break #just in case someone is selling both keywords in the same posting (don't want duplicate messages)
                                                
#to-do, parse post and find price
#to-do, auto-comment + auto-message user
#to-do, handle the finding of more than one keyword better instead of breaking
