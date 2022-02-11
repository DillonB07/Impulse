from __future__ import print_function
import datetime
import os.path
import random
from os import system
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os
import time
import playsound
import speech_recognition as sr
import pyttsx3
import pytz
import subprocess
from pathlib import Path
import requests
import webbrowser


BASE_DIR = Path(__file__).resolve().parent
# USER = 'dillonbarnes'
USER = input('Please enter your username for the computer ie. \'dillonbarnes\': ')
# NICK = 'Dillon'
NICK = input('Please enter the name you would like to be called ie. \'Dillon\': ')

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

MONTHS = ['januray', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
DAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
DAY_EXTENSIONS = ['rd', 'th', 'st', 'nd']


def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
        said = ''

        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            print('Exception: ' + str(+e))

        if said is None:
            get_audio()
        else:
            return said.lower()


def authenticate_google():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                '.credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('calendar', 'v3', credentials=creds)


def get_events(day, service):
    date = datetime.datetime.combine(day, datetime.datetime.min.time())
    end_date = datetime.datetime.combine(day, datetime.datetime.max.time())
    utc = pytz.UTC
    date = date.astimezone(utc)
    end_date = end_date.astimezone(utc)

    events_result = service.events().list(calendarId='primary', timeMin=date.isoformat(), timeMax=end_date.isoformat(),
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    if events := events_result.get('items', []):
        speak(f"You have {len(events)} events on this day.")

        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            start_time = str(start.split("T")[1].split("+")[0])  # get the hour the event starts
            if int(start_time.split(":")[0]) < 12:  # if the event is in the morning
                start_time += "am"
            else:
                start_time = str(int(start_time.split(":")[0]) - 12) + start_time.split(':')[1] # convert 24 hour time to regular
                start_time += "pm"

            speak(f'{event["summary"]} at {start_time}')

    else:
        speak('No upcoming events found.')


def get_date(text):
    text = text.lower()
    today = datetime.date.today()

    if text.count == 'today':
        return today

    day = -1
    day_of_week = -1
    month = -1
    year = today.year

    for word in text.split():
        if word in MONTHS:
            month = MONTHS.index(word) + 1
        elif word in DAYS:
            day_of_week = DAYS.index(word)
        elif word.isdigit():
            day = int(word)
        else:
            for ext in DAY_EXTENSIONS:
                found = word.find(ext)
                if found > 0:
                    try:
                        day = int(word[:found])
                    except:
                        pass

    if month < today.month and month != -1:
        year += 1

    if day < today.day and month == -1 and day != -1:
        month += 1

    if month == -1 and day == -1 and day_of_week != -1:
        current_day_of_week = today.weekday()
        dif = day_of_week - current_day_of_week

        if dif < 0:
            dif += 7
            if text.count('next') >= 1:
                dif += 7

        return today + datetime.timedelta(dif)

    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    if text.count("tomorrow") > 0:
        return tomorrow

    if month == -1 or date == -1:
        return None

    return datetime.date(month=month, day=day, year=year)


def note(text):
    NOTES_DIR = Path(BASE_DIR, 'Notes')
    date = datetime.datetime.now()
    date_name = str(date).replace(':', '-') + '-note.txt'
    file_name = 'Notes/' + str(date).replace(':', '-') + '-note.txt'
    with open(file_name, 'w') as f:
        f.write(text)

    try:
        try:
            texteditor = '/System/Applications/Sublime Text.app/Contents/MacOS/sublime_text'
            file = Path(NOTES_DIR, date_name)
            subprocess.Popen([texteditor, file])
        except Exception as e:
            try:
                texteditor = f'/Users/{USER}/Applications/Sublime Text.app/Contents/MacOS/sublime_text'
                file = Path(NOTES_DIR, date_name)
                subprocess.Popen([texteditor, file])
            except:
                pass
    except:
        speak('Sublime Text not installed')


WAKE = 'impulse'
SERVICE = authenticate_google()
print('Start')

while True:
    def run():
        try:
            WAKE = 'impulse'
            text = get_audio()
            if text.count(WAKE) > 0:
                print('Listening')
                playsound.playsound('.beep.mp3')
                text = get_audio()
                print('.')

                CALENDAR_STRS = ['what do i have', 'do i have plans', 'am i busy', 'events', 'what is on', 'what\'s going on']
                for phrase in CALENDAR_STRS:
                    if phrase in text:
                        if date := get_date(text):
                            get_events(get_date(text), SERVICE)
                        else:
                            speak('Sorry, you need to tell me a date to check.')

                NOTE_STRS = ['write this down', 'note', 'remember this']
                for phrase in NOTE_STRS:
                    if phrase in text:
                        speak('What would you like me to write down?')
                        note_text = get_audio()
                        if note_text != None:
                            note(note_text)
                            speak('I have saved your note')
                        else:
                            speak('Sorry, I couldn\'t hear anything.')

                GREETING_STRS = ['hello', 'hallo', 'hi', 'greetings', 'salutations', 'hey', 'hullo', 'howdy']
                for phrase in GREETING_STRS:
                    if phrase in text:
                        phrase = random.choice([f'Hi {NICK}', f'Hallo {NICK}', f'Howdy {NICK}', f'Salutations {NICK}', f'Hello {NICK}', f'Hey {NICK}'])
                        speak(phrase)

                PARTING_STRS = ['bye', 'goodbye', 'see you later', 'adios', 'see ya']
                for phrase in PARTING_STRS:
                    if phrase in text:
                        phrase = random.choice([f'Goodbye {NICK}', f'See you later {NICK}!', f'Adiós {NICK}', f'I\' miss you {NICK}!'])
                        speak(phrase)

                TIME_STRS = ['time', 'date', 'day']
                for phrase in TIME_STRS:
                    if phrase in text:
                        now = datetime.datetime.now()
                        speak("It is currently: ")
                        speak(now.strftime(f'%H:%M on %A, %B the %dth, %Y {NICK}'))

                THANK_STRS = ['thanks', 'thank you', 'gracias', 'cheers']
                for phrase in THANK_STRS:
                    if phrase in text:
                        phrase = random.choice([f'No problem {NICK}', 'I\'m glad to assist you', f'You\'re welcome {NICK}!', 'My pleasure'])
                        speak(phrase)

                if 'what are you' in text:
                    speak('I\'m Impulse, your Virtual Assistant')

                elif 'family' in text:
                    speak('I have an extremely large family. All of the virtual assistants in the world are my siblings.')

                elif 'joke' in text or 'jokes' in text:
                    import requests

                    url = 'https://official-joke-api.appspot.com/random_joke'

                    response = requests.get(url)
                    js = response.json()
                    setup = js['setup']
                    punchline = js['punchline']
                    # print(response)
                    # print(response.text)
                    speak(setup)
                    print(setup)
                    speak(punchline)
                    print(punchline)

                elif 'google' in text:
                    webbrowser.open_new('https://google.com')
                    speak('I have opened Google in your web browser')

                elif 'exit' in text:
                    speak(f'Goodbye! Come back later {NICK}!')
                    exit(f'See you later! {NICK}')


                else:
                    speak('Sorry, I don\'t understand.')


                print('End')





        except:
            run()

    run()
