from __future__ import print_function

import os.path
import datetime
from sys import argv

import sqlite3

from dateutil import parser

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']

CALENDAR_ID = 'https://calendar.google.com/calendar/embed?src=amanjauni%40gmail.com&ctz=UTC'
TIMEZONE = '(GMT+03:00) East Africa Time'

def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    if len(argv) > 1:
        if argv[1] == 'add':
            duration = argv[2]
            description = argv[3]
            addEvent(creds, duration, description)
        elif argv[1] == 'commit':
            commitHours(creds)
        elif argv[1] == 'list':
            listEvents(creds)
        elif argv[1] == 'delete':
            event_id = argv[2]
            deleteEvent(creds, event_id)

addEvent = input()

def listEvents(creds):
    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId= 'https://calendar.google.com/calendar/embed?src=amanjauni%40gmail.com&ctz=UTC', 
                                              timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"{event['summary']} - {start}")

    except HttpError as error:
        print('An error occurred: %s' % error)

def deleteEvent(creds, event_id):
    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        service.events().delete(calendarId= 'https://calendar.google.com/calendar/embed?src=amanjauni%40gmail.com&ctz=UTC', eventId=event_id).execute()
        print(f"Event {event_id} deleted successfully")

    except HttpError as error:
        print('An error occurred: %s' % error)

def commitHours(creds):
    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        today = datetime.date.today()
        timeStart = str(today) + "T00:00:00Z"
        timeEnd = str(today) + "T23:59:59Z" 
        print("Getting today's meeting hours")

        events_result = service.events().list(calendarId='https://calendar.google.com/calendar/embed?src=amanjauni%40gmail.com&ctz=UTC', 
                                              timeMin=timeStart, timeMax=timeEnd, singleEvents=True, orderBy='startTime', timeZone=TIMEZONE).execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        total_duration = datetime.timedelta(
        seconds=0,
        minutes=0,
        hours=0,
        )
        id = 0
        print("MEETING HOURS:")
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))

            start_formatted = parser.isoparse(start) 
            end_formatted = parser.isoparse(end) 
            duration = end_formatted - start_formatted
            total_duration += duration
            print(f"{event['summary']}, duration: {duration}")
        print(f"Total meeting time: {total_duration}")

        conn = sqlite3.connect('hours.db')
        cur = conn.cursor()
        print("Opened database successfully")
        date = datetime.date.today()

        formatted_total_duration = total_duration.seconds/60/60
        meeting_hours = (date, 'MEETING', formatted_total_duration) 
        cur.execute("INSERT INTO hours VALUES(?, ?, ?);", meeting_hours)
        conn.commit()
        print("Meeting hours added to database successfully")
    except HttpError:
        print("Error occured")

print(main())