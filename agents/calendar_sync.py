import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]

CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), '../credentials.json')
TOKEN_PATH = os.path.join(os.path.dirname(__file__), '../token.json')

def get_calendar_service():
    """Shows basic usage of the Google Calendar API."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDENTIALS_PATH):
                print(f"Warning: {CREDENTIALS_PATH} not found. Calendar sync will be mocked.")
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def fetch_todays_events():
    """Fetches events for the current day."""
    service = get_calendar_service()
    if not service:
        # Mock data if no service
        return ["Mock Event: Sambo Training at 18:00", "Mock Event: Deep Work at 20:00"]

    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    
    # Get start and end of today
    today_start = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + "Z"
    today_end = datetime.datetime.now().replace(hour=23, minute=59, second=59, microsecond=999).isoformat() + "Z"

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=today_start,
            timeMax=today_end,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])

    event_summary = []
    if not events:
        print("No upcoming events found.")
    else:
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            event_summary.append(f"{event['summary']} at {start}")

    return event_summary

def block_time_for_deep_work(start_time, end_time, summary="The Deep Build"):
    """Blocks time in the calendar."""
    service = get_calendar_service()
    if not service:
        print(f"[MOCK] Blocking time: {summary} from {start_time} to {end_time}")
        return

    event = {
        'summary': summary,
        'description': 'Scheduled by Shadow System',
        'start': {
            'dateTime': start_time,
            'timeZone': 'UTC', # Adjust safely
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'UTC',
        },
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print(f"Event created: {event.get('htmlLink')}")

if __name__ == "__main__":
    events = fetch_todays_events()
    print("Today's Events:", events)
