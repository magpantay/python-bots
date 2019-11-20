import praw
import time
import datetime
import sys

is_hws = 0  # a switch whether this is the hws_bot or the bapcs_bot


def convert_epoch_to_date(sub_time):
	time0 = datetime.datetime.fromtimestamp(sub_time)

	# the following is used to convert from UTC to PST -8 (I guess the long way), at least I don't need to import pytz or something

	month_sub_factor = 0
	day_sub_factor = 0
	year_sub_factor = 0
	hour_sub_factor = 8

	if time0.hour - hour_sub_factor < 0:
		day_sub_factor = 1
		hour_sub_factor = 8 - 24
		if time0.day - day_sub_factor < 1:
			month_sub_factor = 1
			if time0.month == 2 and time0.year % 4 != 0:
				day_sub_factor = 1 - 28
			elif time0.month == 2 and time0.year % 4 == 0:
				day_sub_factor = 1 - 29
			elif time0.month != 1 or time0.month != 3 or time0.month != 5 or time0.month != 7 or time0.month != 8 or time0.month != 10 or time0.month != 12:
				day_sub_factor = 1 - 30
			else:
				day_sub_factor = 1 - 31
			if time0.month - month_sub_factor < 1:
				month_sub_factor = 1 - 12
				year_sub_factor = 1

	# the following is used to convert from military-styled timing to AM/PM styled timing

	PM = 0  # boolean for if AM or PM
	if time0.hour - hour_sub_factor > 12:
		hour_sub_factor = hour_sub_factor + 12  # subtracts 12, switches to PM
		PM = 1

	if PM:
		# :02 prints minimum 2 digits
		return "{0:02}-{1:02}-{2:02} at {3:02}:{4:02}:{5:02}PM PST".format(time0.month - month_sub_factor, time0.day - day_sub_factor, time0.year - year_sub_factor, time0.hour - hour_sub_factor, time0.minute, time0.second)
	else:
		# :02 prints minimum 2 digits
		return "{0:02}-{1:02}-{2:02} at {3:02}:{4:02}:{5:02}AM PST".format(time0.month - month_sub_factor, time0.day - day_sub_factor, time0.year - year_sub_factor, time0.hour - hour_sub_factor, time0.minute, time0.second)


def print_and_send_post(username, bot, subreddit, submission, found_keyword, hws_yes):
        if hws_yes:
            print("Flair: {0}\nTitle: {1}\nAuthor: /u/{2}\nURL: {3}\nTime: {4}\n".format(submission.link_flair_text,
                  submission.title, submission.author, submission.url, convert_epoch_to_date(submission.created)))
            subject_content = "[FROM BOT] Found {0} You May Want From {1}!".format(
                found_keyword.upper(), subreddit.display_name)
            message_content = "Flair: {0}\n\nTitle: {1}\n\nAuthor: /u/{2}\n\nURL: {3}\n\nTime: {4}\n\n".format(
                submission.link_flair_text, submission.title, submission.author, submission.url, convert_epoch_to_date(submission.created))
            bot.redditor(username).message(subject_content, message_content)
        else:  # bapcs_format
            print("Title: {0}\nURL: {1}\nTime: {2}\n".format(
                submission.title, submission.url, convert_epoch_to_date(submission.created)))
            subject_content = "[FROM BOT] Found {0} You May Want From {1}!".format(
                found_keyword.upper(), subreddit.display_name)
            message_content = "Title: {0}\n\nURL: {1}\n\nTime: {2}\n\n".format(
                submission.title, submission.url, convert_epoch_to_date(submission.created))
            bot.redditor(username).message(subject_content, message_content)


def check_locality(submission_title, locality_country, locality_state):
    if locality_state == '' and locality_country != '':
        return ((submission_title.lower().find("local") != -1 and submission_title.lower().find("paypal") == -1) and (submission_title.find(locality_country) != -1 or submission_title.find(locality_country) != -1)) or (submission_title.lower().find("paypal") != -1 and submission_title.find(locality_country))
    elif locality_state == '' and locality_country == 'USA':
        print("USA Locality Detected.\nNo postings will be returned, please quit the program and enter your state.\n")
        return 0
    else:
        return ((submission_title.lower().find("local") != -1 and submission_title.lower().find("paypal") == -1) and (submission_title.find(locality_country + "-" + locality_state) != -1 or submission_title.find(locality_country + " - " + locality_state) != -1)) or (submission_title.lower().find("paypal") != -1 and submission_title.find(locality_country))
    # finds "Local", doesn't find "Paypal", but in locality --OR-- it just finds "paypal" and is within country (and [optionally] state)


def flair_check(submission, hws_yes):
    if hws_yes:
        # including "None" in the case it catches possible selling item that isn't marked yet
        return submission.link_flair_text == "Selling" or submission.link_flair_text == "None"
    else:
        return submission.link_flair_text != "Out of Stock" or submission.link_flair_text != "Expired"


def entry_not_found(entry_name):
  print("{0} entry not found. Try again.\n".format(entry_name))
  sys.exit()

########################


def ignore_alert(submission_title, reason):
    print("##########\n[IGNORED]\nTitle: {0}\nReason:{1}\n##########\n".format(
        submission_title, reason))
########################


def main():
	print("Location of Praw: {0}\n".format(praw.__path__))

	if is_hws:
		bot = praw.Reddit(
		    'bot1', user_agent='HWS/BAPCS Bot v2.1 [Mode: HWS]', site_name='hws_bot')
	else:
		bot = praw.Reddit(
		    'bot2', user_agent='HWS/BAPCS Bot v2.1 [Mode: BAPCS]', site_name='bapcs_bot')

	if is_hws:
		subreddit = bot.subreddit('hardwareswap')
		config_file = open("hws_bot.ini", "r")
	else:
		subreddit = bot.subreddit('buildapcsales')
		config_file = open("bapcs_bot.ini", "r")

	config_file_contents = config_file.read()
	config_file.close()

	if config_file_contents.find("keywords=['") == -1:
		entry_not_found("Keywords")
	elif config_file_contents.find("antikeywords=['") == -1:
		entry_not_found("Anti-keywords")
	elif config_file_contents.find("sendTo='") == -1:
		entry_not_found("User to send to (sendTo)")
	elif is_hws and config_file_contents.find("country='") == -1:
		entry_not_found("Country")
	else:
		keywords_raw = config_file_contents.split("keywords=['")[1]
		keywords_raw = keywords_raw.split("']")[0]
		keywords = keywords_raw.split("','")

		antikeywords_raw = config_file_contents.split("antikeywords=['")[1]
		antikeywords_raw = antikeywords_raw.split("']")[0]
		antikeywords = antikeywords_raw.split("','")

		sendTo = config_file_contents.split("sendTo='")[1]
		sendTo = sendTo.split("'")[0]

	if is_hws:
		  country = config_file_contents.split("country='")[1]
		  country = country.split("'")[0]

		  if config_file_contents.find("state='") != -1:
			  state = config_file_contents.split("state='")[1]
			  state = state.split("'")[0]
		  else:
			  state = ""

	for submission in subreddit.stream.submissions():
		ignore_post = 0
		if flair_check(submission, is_hws):
			if is_hws:  # because checking locality is an hws_bot specific thing
				if check_locality(submission.title, country, state) != 1: #if the locality check fails
					continue #ignore this one
				for i in range(len(keywords)):
					if submission.title.lower().find(keywords[i]) != -1:
						for j in range(len(antikeywords)):
							if submission.title.lower().find(antikeywords[j]) != -1:
								ignore_post = 1
								break #we only need one ignore
						if ignore_post != 1:
							print_and_send_post(sendTo, bot, subreddit, submission, keywords[i], is_hws)
							break #just in case someone is selling both keywords in the same posting (don't want duplicate messages)
			else:
				for i in range(len(keywords)):
					if submission.title.lower().find(keywords[i]) != -1:
						for j in range(len(antikeywords)):
							if submission.title.lower().find(antikeywords[j]) != -1:
								ignore_post = 1
								break #we only need one ignore
						if ignore_post != 1:
							print_and_send_post(sendTo, bot, subreddit, submission, keywords[i], is_hws)
							break #just in case someone is selling both keywords in the same posting (don't want duplicate messages)

if __name__ == "__main__":
	main()
# to-do, parse post and find price
# to-do, auto-comment + auto-message user
# to-do, handle the finding of more than one keyword better instead of breaking
