from datetime import timedelta

import google.auth
import googleapiclient.discovery

from config.base import CALENDAR_ID


def add_days(date, days):
    """
    日付に指定された日数を加算する関数です。
    :param date: 元の日付
    :param days: 加算する日数
    :return: 加算後の日付
    """
    return date + timedelta(days=days)


def register_event(event_date):
    """
    Googleカレンダーに予定を登録する関数です。
    :param event_date: 予定の日付
    :return: 登録された予定のID
    """

    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = google.auth.load_credentials_from_file('credentials.json', SCOPES)[0]
    service = googleapiclient.discovery.build('calendar', 'v3', credentials=creds)

    start_time = (event_date + timedelta(hours=21)).strftime('%Y-%m-%dT%H:%M:%S')
    end_time = (event_date + timedelta(hours=21, minutes=30)).strftime('%Y-%m-%dT%H:%M:%S')

    event = {
        'summary': 'パンツェッタ',
        'start': {
            'dateTime': start_time,
            'timeZone': 'Japan'
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'Japan'
        }
    }

    created_event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
    event_id = created_event.get('id')
    return event_id
