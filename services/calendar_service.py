"""
Calendar service for the surgery scheduling application.

This module provides a service for integrating with Google Calendar.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
import time
from unittest.mock import MagicMock

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

from services.exceptions import CalendarError, ConfigurationError
from services.logger_config import logger

# Define the scopes needed for the Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']


class CalendarService:
    """
    Service for integrating with Google Calendar.

    This service provides methods for creating, updating, and deleting
    events in Google Calendar.
    """

    def __init__(self, token_path='token.json', credentials_path='credentials.json', testing=False):
        """
        Initialize the calendar service.

        Args:
            token_path: Path to the token file.
            credentials_path: Path to the credentials file.
            testing: Whether the service is being used in a test environment.

        Raises:
            ConfigurationError: If the credentials file is not found.
            CalendarError: If authentication fails.
        """
        self.token_path = token_path
        self.credentials_path = credentials_path
        self.credentials = None
        self.service = None
        self.timezone = os.getenv('CALENDAR_TIMEZONE', 'America/New_York')
        self.testing = testing or os.getenv('TESTING', 'False').lower() in ('true', '1', 't')

        # Authenticate and build the service
        if not self.testing:
            self._authenticate()
        else:
            # In testing mode, create a mock service
            logger.info("Using mock calendar service for testing")
            self.service = MagicMock()

    def _authenticate(self):
        """
        Authenticate with Google Calendar API.

        This method handles the OAuth 2.0 flow for authentication.

        Raises:
            ConfigurationError: If the credentials file is not found.
            CalendarError: If authentication fails.
        """
        try:
            # Check if token.json exists
            if os.path.exists(self.token_path):
                self.credentials = Credentials.from_authorized_user_file(
                    self.token_path, SCOPES
                )

            # If there are no valid credentials, let's get some
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    # Refresh the token if it's expired
                    self.credentials.refresh(Request())
                else:
                    # If no valid credentials are available, run the OAuth flow
                    if not os.path.exists(self.credentials_path):
                        raise ConfigurationError(
                            f"Credentials file not found at {self.credentials_path}"
                        )

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    self.credentials = flow.run_local_server(port=0)

                # Save the credentials for the next run
                with open(self.token_path, 'w') as token:
                    token.write(self.credentials.to_json())

            # Build the service
            self.service = build('calendar', 'v3', credentials=self.credentials)
            logger.info("Successfully authenticated with Google Calendar API")

        except Exception as e:
            logger.error(f"Error authenticating with Google Calendar API: {e}")
            raise CalendarError("Failed to authenticate with Google Calendar API", e)

    def create_event(
        self,
        calendar_id: str,
        summary: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        location: Optional[str] = None,
        attendees: Optional[List[Dict[str, str]]] = None,
        reminders: Optional[Dict[str, Any]] = None,
        color_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new event in Google Calendar.

        Args:
            calendar_id: The ID of the calendar.
            summary: The summary (title) of the event.
            description: The description of the event.
            start_time: The start time of the event.
            end_time: The end time of the event.
            location: The location of the event.
            attendees: A list of attendees.
            reminders: Reminder settings.
            color_id: The color ID for the event.

        Returns:
            The created event.

        Raises:
            CalendarError: If the event cannot be created.
        """
        try:
            # Create the event body
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': self.timezone
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': self.timezone
                }
            }

            # Add optional fields if provided
            if location:
                event['location'] = location

            if attendees:
                event['attendees'] = attendees

            if reminders:
                event['reminders'] = reminders
            else:
                # Default reminders
                event['reminders'] = {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 60}  # 1 hour before
                    ]
                }

            if color_id:
                event['colorId'] = color_id

            # Create the event
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()

            logger.info(
                f"Event created: {created_event.get('htmlLink')} "
                f"for {start_time.strftime('%Y-%m-%d %H:%M')}"
            )

            return created_event

        except HttpError as e:
            logger.error(f"Error creating event: {e}")
            raise CalendarError("Failed to create event", e)

        except Exception as e:
            logger.error(f"Unexpected error creating event: {e}")
            raise CalendarError("Unexpected error creating event", e)

    def update_event(
        self,
        calendar_id: str,
        event_id: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        location: Optional[str] = None,
        attendees: Optional[List[Dict[str, str]]] = None,
        reminders: Optional[Dict[str, Any]] = None,
        color_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing event in Google Calendar.

        Args:
            calendar_id: The ID of the calendar.
            event_id: The ID of the event to update.
            summary: The summary (title) of the event.
            description: The description of the event.
            start_time: The start time of the event.
            end_time: The end time of the event.
            location: The location of the event.
            attendees: A list of attendees.
            reminders: Reminder settings.
            color_id: The color ID for the event.

        Returns:
            The updated event.

        Raises:
            CalendarError: If the event cannot be updated.
        """
        try:
            # Get the existing event
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            # Update fields if provided
            if summary:
                event['summary'] = summary

            if description:
                event['description'] = description

            if start_time:
                event['start'] = {
                    'dateTime': start_time.isoformat(),
                    'timeZone': self.timezone
                }

            if end_time:
                event['end'] = {
                    'dateTime': end_time.isoformat(),
                    'timeZone': self.timezone
                }

            if location:
                event['location'] = location

            if attendees:
                event['attendees'] = attendees

            if reminders:
                event['reminders'] = reminders

            if color_id:
                event['colorId'] = color_id

            # Update the event
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()

            logger.info(
                f"Event updated: {updated_event.get('htmlLink')} "
                f"for {event['start'].get('dateTime')}"
            )

            return updated_event

        except HttpError as e:
            logger.error(f"Error updating event: {e}")
            raise CalendarError("Failed to update event", e)

        except Exception as e:
            logger.error(f"Unexpected error updating event: {e}")
            raise CalendarError("Unexpected error updating event", e)

    def delete_event(self, calendar_id: str, event_id: str) -> bool:
        """
        Delete an event from Google Calendar.

        Args:
            calendar_id: The ID of the calendar.
            event_id: The ID of the event to delete.

        Returns:
            True if the event was deleted, False otherwise.

        Raises:
            CalendarError: If the event cannot be deleted.
        """
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()

            logger.info(f"Event {event_id} deleted from calendar {calendar_id}")
            return True

        except HttpError as e:
            if e.resp.status == 404:
                logger.warning(f"Event {event_id} not found in calendar {calendar_id}")
                return False

            logger.error(f"Error deleting event: {e}")
            raise CalendarError("Failed to delete event", e)

        except Exception as e:
            logger.error(f"Unexpected error deleting event: {e}")
            raise CalendarError("Unexpected error deleting event", e)

    def get_events(
        self,
        calendar_id: str,
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 100,
        query: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get events from Google Calendar.

        Args:
            calendar_id: The ID of the calendar.
            time_min: The minimum time to include.
            time_max: The maximum time to include.
            max_results: The maximum number of results to return.
            query: A free text search query.

        Returns:
            A list of events.

        Raises:
            CalendarError: If the events cannot be retrieved.
        """
        try:
            # Set default time range if not provided
            if not time_min:
                time_min = datetime.now()

            if not time_max:
                time_max = time_min + timedelta(days=30)

            # Build the request
            request = {
                'calendarId': calendar_id,
                'timeMin': time_min.isoformat() + 'Z',  # 'Z' indicates UTC time
                'timeMax': time_max.isoformat() + 'Z',
                'maxResults': max_results,
                'singleEvents': True,
                'orderBy': 'startTime'
            }

            if query:
                request['q'] = query

            # Get the events
            events_result = self.service.events().list(**request).execute()
            events = events_result.get('items', [])

            logger.info(f"Retrieved {len(events)} events from calendar {calendar_id}")
            return events

        except HttpError as e:
            logger.error(f"Error retrieving events: {e}")
            raise CalendarError("Failed to retrieve events", e)

        except Exception as e:
            logger.error(f"Unexpected error retrieving events: {e}")
            raise CalendarError("Unexpected error retrieving events", e)

    def update_surgeon_calendar(self, surgeon, original_surgery, new_surgery):
        """
        Update a surgeon's calendar with surgery information.

        Args:
            surgeon: The surgeon object.
            original_surgery: The original surgery object (can be None).
            new_surgery: The new surgery object.

        Raises:
            CalendarError: If the calendar cannot be updated.
        """
        try:
            # Check if surgeon has a calendar ID
            if not hasattr(surgeon, 'calendar_id') or not surgeon.calendar_id:
                logger.warning(f"Surgeon {surgeon.name} does not have a calendar ID")
                return

            # Step 1: Delete the original surgery event if it exists
            if original_surgery and hasattr(original_surgery, 'calendar_event_id') and original_surgery.calendar_event_id:
                try:
                    self.delete_event(surgeon.calendar_id, original_surgery.calendar_event_id)
                    logger.info(f"Original surgery event {original_surgery.surgery_id} deleted")
                except Exception as e:
                    logger.error(f"Error deleting original surgery event: {e}")

            # Step 2: Create a new event for the new surgery
            if not hasattr(new_surgery, 'start_time') or not new_surgery.start_time:
                logger.warning(f"Surgery {new_surgery.surgery_id} does not have a start time")
                return

            # Calculate end time based on duration
            end_time = new_surgery.start_time + timedelta(minutes=new_surgery.duration_minutes)

            # Create event
            event = self.create_event(
                calendar_id=surgeon.calendar_id,
                summary=f"Surgery: {new_surgery.surgery_type_details.name if hasattr(new_surgery, 'surgery_type_details') else 'Unknown'}",
                description=f"Surgery ID: {new_surgery.surgery_id}\nPatient ID: {new_surgery.patient_id if hasattr(new_surgery, 'patient_id') else 'Unknown'}\nRoom: {new_surgery.room.location if hasattr(new_surgery, 'room') else 'Unknown'}",
                start_time=new_surgery.start_time,
                end_time=end_time,
                location=new_surgery.room.location if hasattr(new_surgery, 'room') else None,
                color_id="11"  # Use a specific color for surgeries (11 is red)
            )

            # Store the event ID in the surgery object if possible
            if hasattr(new_surgery, 'calendar_event_id'):
                new_surgery.calendar_event_id = event['id']

            logger.info(f"New surgery event {new_surgery.surgery_id} added to calendar")

        except Exception as e:
            logger.error(f"Error updating calendar for surgeon {surgeon.name}: {e}")
            raise CalendarError(f"Failed to update calendar for surgeon {surgeon.name}", e)
