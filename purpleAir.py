###############################################################################
######################## PurpleAir Watchdog Algorithm #########################
###############################################################################

##### Created by: Philip Orlando
##### Sustainable Atmospheres Research Lab
##### Portland State University
##### 2018-02-15

import json
import urllib
import requests
import time
from datetime import datetime
import calendar
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import getpass
import pyfiglet
import termcolor
import itertools
import sys

## program header
termcolor.cprint(pyfiglet.figlet_format('PurpleAir\nWatchdog', font='slant'),
	'magenta', attrs=['bold'])

## create send email Class
class Gmail(object):
	def __init__(self, email, recipient, password):
		self.email = email
		self.password = password
		self.recipient = recipient
		self.server = 'smtp.gmail.com'
		self.port = 587
		session = smtplib.SMTP(self.server, self.port)
		session.ehlo()
		session.starttls()
		session.ehlo
		session.login(self.email, self.password)
		self.session = session

	def send_message(self, subject, body):

		headers = [
			"From: " + self.email,
			"Subject: " + subject,
			"To: " + self.recipient,
			"MIME-Version: 1.0",
			"Content-Type: text/html"]

		headers = "\r\n".join(headers)
		self.session.sendmail(
			self.email,
			self.recipient,
			headers + "\r\n\r\n" + body)


## define email parameters:
sender = 'phlp.orlando@gmail.com'

##recipient = 'h6lg@pdx.edu'
recipient = 'porlando@pdx.edu'

## secured raw_input for email password
email_password = getpass.getpass('[*] Enter the email server password: ')

## creating a list of sensor IDs
sensorID = [3786 ## PSU Star Lab Cully
	,3787 ## PSU Star Lab Cully B
	#,3357 ## Irvington
	#,3358 ## Irvington B
	#,5826 ## NE 12th & Tillamook
	#,5827 ## NE 12th & Tillamook B
	#,7018 ## Miller
	#,7019 ## Miller B
	#,2317 ## Portsmouth Portland
	#,2318 ## Portsmouth Portland B
	,2037 ## PSU STAR Lab Hayden Island
	,2038 ## PSU STAR Lab Hayden Island B
	,1606 ## PSU STAR Lab Roof North
	,1607 ## PSU STAR Lab Roof North B
	,1569 ## PSU STAR Lab Roof South
	,1570 ## PSU STAR Lab Roof South B
	,7386 ## PSU STAR Lab Roof South SD
	,7387 ## PSU STAR Lab Roof South SD B
	,2045 ## PSU STAR Lab Rose City Park
	,2046 ## PSU STAR Lab Rose City Park B
	,2065 ## STAR Lab Hillsdale
	,2066 ## STAR Lab Hillsdale
	,2059 ## STAR Lab Aloha
	,2060 ## STAR Lab Aloha B
	,2055 ## STAR LAB BETHANY
	,2056 ## STAR LAB BETHANY B
	,2043 ## STAR Lab Creston Kenilworth
	,2044 ## STAR Lab Creston Kenilworth B
	,2057 ## STAR Lab Homestead Neighborhood
	,2058 ## STAR Lab Homestead Neighborhood B
	,2053 ## STAR Lab Powell-Hurst Gilbert
	,2054 ## Star Lab Powell0Hurst Gilbert B
	,3707 ## STAR Jesuit HS
	,3708 ## STAR Jesuit HS B
	,3729 ## PSU STAR Lab Edgewater
	,3730 ## PSU STAR Lab Edgewater B
	,3684 ## Lower Boones Ferry
	,3685 ## Lower Boones Ferry B
	,3775 ## PSU STAR Lab Lost Park
	,3776 ## PSU STAR Lab Lost Park B
	#,2033 ## Star Lab Jesuit
	#,2034 ## Star Lab Jesuit B

	#,2566 ## VerdeVista
	#,2567 ## VerdeVista B
	#,3404 ## Woods Park
	#,3405 ## Woods Park B
	#,3281 ## Red Fox Hills
	#,3282 ## Red Fox Hills B
	#,3233 ## Marion Court Apartments
	#,3234 ## Marion Court Apartments B
	#,2741 ## College Park
	#,2742 ## College Park B
	]


## establish downtime intervals
downHour = int(60**2)
downDay = int(60*60*24)
#downDay = int(60)
#sleep_time = int(30)
sleep_time = int(60*15) ## 15-minute scan

## wrap our algo into a while loop:
while True:

	## retrieving the current timestamp and converting it to unixtime
	t = datetime.utcnow()
	startTime = calendar.timegm(t.utctimetuple())
	nextDay = startTime + downDay

	try:
		del(offline_sensors[:])

	except Exception:
		pass

	offline_sensors = []

	while  calendar.timegm(datetime.utcnow().utctimetuple()) < nextDay:

		d = datetime.utcnow()
		unixtime = calendar.timegm(d.utctimetuple())

		print

		## assigning PurpleAir API to url
		url = "https://www.purpleair.com/json"

		## GET request from PurpleAir API
		try:
			r = requests.get(url)
			print '[*] Connecting to API...'
			print '[*] GET Status: ', r.status_code

		except Exception as e:
			print '[*] Unable to connect to API...'
			print 'GET Status: ', r.status_code
			print e
		print


		try:
			## parse the JSON returned from the request
			j = r.json()
		except Exception as e:
			print '[*] Unable to parse JSON'
			print e

		try:

			##  iterate through entire dictionary
			for sensor in j['results']:

				## retrieve only the sensors from our list
				if sensor['ID'] in sensorID:

					## determine if a sensor has been down for a day
					if (unixtime - int(sensor['LastSeen'])) > downHour and sensor['ID'] not in [int(y) for x in offline_sensors for y in x.split()]:
						print '[*] Sensor', sensor['Label'], 'went offline at', datetime.fromtimestamp(sensor['LastSeen'])
						down_sensor = str(sensor['Label'])
						down_ID = str(sensor['ID'])
						offline_sensors.append(down_ID) ## this could be better handled with files, avoiding dupe emails when restarting the program more than once per day (if needed due to an exception)
						## send email
						msg = 'has been down since ' + str(datetime.fromtimestamp(sensor['LastSeen']))
						gm = Gmail(sender, recipient,  email_password)
						gm.send_message(down_sensor, msg)
						print '[*] Notification sent.'

					elif (unixtime - int(sensor['LastSeen'])) > downHour and sensor['ID'] in [int(y) for x in offline_sensors for y in x.split()]:
						print '[*] Sensor', sensor['Label'], 'has been down since', datetime.fromtimestamp(sensor['LastSeen'])
						print '[*] Notification has already been sent to', recipient

					else:
						print '[*]', str(sensor['Label']) + ':', sensor['ID'], 'lastSeen', datetime.fromtimestamp(sensor['LastSeen'])

						try:
							offline_sensors.remove(sensor['ID']) # clear a sensor once it goes back online!

						except:
							pass
			print
			print '[*] nextScan', datetime.fromtimestamp(unixtime + sleep_time)
			print '[*] startTime', datetime.fromtimestamp(startTime)
			print '[*] unixtime', datetime.fromtimestamp(unixtime)
			print '[*] nextDay', datetime.fromtimestamp(nextDay)
			time.sleep(sleep_time)

		except Exception as e:
			print '[*] Delivery to ', recipient, 'failed!'
			print e
			print '[*] Will try again in one hour....'
			time.sleep(sleep_time)

	# empty our list of offline sensors each day
	#offline_sensors[:] = []
