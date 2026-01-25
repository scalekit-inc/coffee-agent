from typing import Dict, Any
import logging
from utils import convert_scalekit_response
from scalekit.common.exceptions import ScalekitNotFoundException
from scalekit_client import get_connect

logger = logging.getLogger(__name__)

class CalendarIntegration:
    def __init__(self, user_id="default_user"):
        # Use shared ScaleKit client instead of creating a new one
        self.connect = get_connect()
        self.is_enabled = False
        self.user_id = user_id
    
    def enable(self) -> Dict[str, Any]:
        """Enable Google Calendar integration and get authorization link if needed"""
        try:
            response = self.connect.get_connected_account(
                connection_name="googlecalendar",
                identifier=self.user_id
            )
            
            if response.connected_account.status == "ACTIVE":
                self.is_enabled = True
                return {"success": True, "message": "Google Calendar is already connected!", "status": "connected"}
            else:
                link_response = self.connect.get_authorization_link(
                    connection_name="googlecalendar",
                    identifier=self.user_id
                )
                return {"success": True, "auth_link": link_response.link, "status": "needs_auth"}
                
        except Exception as e:
            logger.info(f"Calendar account check failed for user {self.user_id}, getting auth link: {str(e)}")
            try:
                link_response = self.connect.get_authorization_link(
                    connection_name="googlecalendar",
                    identifier=self.user_id
                )
                return {"success": True, "auth_link": link_response.link, "status": "needs_auth"}
            except Exception as link_error:
                logger.error(f"Failed to get Calendar authorization link for user {self.user_id}: {str(link_error)}", exc_info=True)
                return {"success": False, "message": f"Failed to get authorization link: {str(link_error)}", "status": "error"}
    
    def check_status(self) -> Dict[str, Any]:
        """Check current Google Calendar connection status"""
        try:
            response = self.connect.get_connected_account(
                connection_name="googlecalendar",
                identifier=self.user_id
            )
            
            if response.connected_account.status == "ACTIVE":
                self.is_enabled = True
                return {"success": True, "enabled": True, "status": "connected"}
            else:
                self.is_enabled = False
                return {"success": True, "enabled": False, "status": "disconnected"}
                
        except ScalekitNotFoundException:
            # Expected when Calendar is not configured or user hasn't connected yet
            logger.debug(f"Calendar connection not found for user {self.user_id} (this is expected if Calendar is not configured or not connected)")
            self.is_enabled = False
            return {"success": True, "enabled": False, "status": "not_connected"}
        except Exception as e:
            logger.warning(f"Failed to check Calendar status for user {self.user_id}: {str(e)}", exc_info=True)
            self.is_enabled = False
            return {"success": False, "enabled": False, "status": "error"}
    
    def fetch_events(self, max_results: int = 10, query: str = "", time_min: str = "", time_max: str = "") -> Dict[str, Any]:
        """Fetch calendar events from Google Calendar"""
        if not self.is_enabled:
            return {
                "success": False,
                "message": "Google Calendar integration is not enabled",
                "status": "disabled"
            }
        
        try:
            # Debug: Log the parameters being sent
            logger.debug(f"Calendar fetch parameters - time_min: {time_min}, time_max: {time_max}, query: {query}")
            
            # Validate that time parameters are set for date-specific queries
            if not time_min or not time_max:
                logger.warning(f"time_min or time_max is empty! This may cause incorrect date filtering.")
            
            # Add timezone information to debug
            if time_min and time_max:
                try:
                    from datetime import datetime, timezone
                    
                    # Parse the times and show local timezone equivalents
                    utc_min = datetime.fromisoformat(time_min.replace('Z', '+00:00'))
                    utc_max = datetime.fromisoformat(time_max.replace('Z', '+00:00'))
                    
                    # Show in common timezones using built-in timezone handling
                    logger.debug(f"Timezone info - time_min: {time_min} (UTC)")
                    logger.debug(f"Timezone info - time_min: {utc_min.strftime('%Y-%m-%d %H:%M:%S')} UTC")
                    
                    # Convert to local system timezone
                    import time
                    local_offset = time.timezone if time.daylight == 0 else time.altzone
                    local_hours = int(local_offset / 3600)
                    local_minutes = int((local_offset % 3600) / 60)
                    local_sign = '+' if local_offset < 0 else '-'
                    
                    local_min = utc_min.replace(tzinfo=timezone.utc).astimezone()
                    logger.debug(f"Timezone info - time_min: {local_min.strftime('%Y-%m-%d %H:%M:%S %Z')} (Local)")
                    
                except Exception as e:
                    logger.debug(f"Could not parse timezone info: {e}")
            
            tool_input = {
                "calendar_id": "primary",
                "max_results": str(max_results),
                "order_by": "startTime",
                "page_token": "",
                "query": query,
                "schema_version": "",
                "single_events": True,
                "time_max": time_max,
                "time_min": time_min,
                "tool_version": ""
            }
            
            logger.debug(f"Tool input being sent: {tool_input}")
            
            # Add timezone summary
            logger.debug(f"TIMEZONE SUMMARY - All API calls use UTC (Z suffix)")
            logger.debug(f"TIMEZONE SUMMARY - time_min: {time_min} = Start of day in UTC")
            logger.debug(f"TIMEZONE SUMMARY - time_max: {time_max} = Start of next day in UTC")
            logger.debug(f"TIMEZONE SUMMARY - This ensures full 24-hour coverage of the requested date")
            
            response = self.connect.execute_tool(
                tool_name="googlecalendar_list_events",
                identifier=self.user_id,
                tool_input=tool_input
            )
            
            # Convert response to dict
            response_dict = convert_scalekit_response(response)
            
            # Debug: Log the response structure
            logger.debug(f"Response structure: {response_dict.keys() if isinstance(response_dict, dict) else 'Not a dict'}")
            if isinstance(response_dict, dict) and 'data' in response_dict:
                logger.debug(f"Data keys: {response_dict['data'].keys() if isinstance(response_dict['data'], dict) else 'Not a dict'}")
            
            # Extract events from ScaleKit structure: data.events
            events_list = []
            if isinstance(response_dict, dict) and 'data' in response_dict:
                if 'events' in response_dict['data']:
                    events_list = response_dict['data']['events']
                    logger.debug(f"Found {len(events_list)} events in response")
            
            # Process events to extract key information for better AI understanding
            if events_list:
                processed_events = []
                for event in events_list:
                    processed_event = {
                        'id': event.get('id'),
                        'summary': event.get('summary', 'No Title'),
                        'description': event.get('description', ''),
                        'start': event.get('start', {}),
                        'end': event.get('end', {}),
                        'organizer': event.get('organizer', {}),
                        'attendees': event.get('attendees', []),
                        'conferenceData': event.get('conferenceData', {}),
                        'htmlLink': event.get('htmlLink', ''),
                        'status': event.get('status', ''),
                        'created': event.get('created', ''),
                        'updated': event.get('updated', '')
                    }
                    
                    processed_events.append(processed_event)
                
                return {
                    "success": True,
                    "events": processed_events,
                    "message": f"Successfully fetched {len(processed_events)} calendar events"
                }
            
            return {
                "success": True,
                "events": events_list if events_list else response_dict,
                "message": f"Successfully fetched {len(events_list) if events_list else max_results} calendar events"
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch calendar events for user {self.user_id}: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to fetch calendar events: {str(e)}",
                "status": "error"
            }
    
    def create_event(self, summary: str, start_datetime: str, event_duration_minutes: int = 30, 
                     description: str = "", location: str = "", attendees_emails: str = "", 
                     calendar_id: str = "primary") -> Dict[str, Any]:
        """Create a new calendar event in Google Calendar"""
        if not self.is_enabled:
            return {
                "success": False,
                "message": "Google Calendar integration is not enabled",
                "status": "disabled"
            }
        
        try:
            # Debug: Log the parameters being sent
            logger.debug(f"Calendar create event parameters - summary: {summary}, start_datetime: {start_datetime}, duration: {event_duration_minutes} minutes")
            
            # Validate timezone conversion
            if not start_datetime.endswith('Z'):
                logger.warning(f"start_datetime should end with 'Z' for UTC timezone: {start_datetime}")
            
            tool_input = {
                "start_datetime": start_datetime,
                "summary": summary,
                "attendees_emails": attendees_emails,
                "calendar_id": calendar_id,
                "create_meeting_room": False,
                "description": description,
                "event_duration_hour": "",
                "event_duration_minutes": str(event_duration_minutes),
                "event_type": "default",
                "guests_can_invite_others": False,
                "guests_can_modify": False,
                "guests_can_see_other_guests": False,
                "location": location,
                "recurrence": "",
                "schema_version": "",
                "send_updates": False,
                "timezone": "UTC",
                "tool_version": "",
                "transparency": "opaque",
                "visibility": "default"
            }
            
            logger.debug(f"Tool input being sent: {tool_input}")
            
            response = self.connect.execute_tool(
                tool_name="googlecalendar_create_event",
                identifier=self.user_id,
                tool_input=tool_input
            )
            
            # Convert response to dict
            response_dict = convert_scalekit_response(response)
            
            # Debug: Log the response structure
            logger.debug(f"Response structure: {response_dict.keys() if isinstance(response_dict, dict) else 'Not a dict'}")
            
            # Extract event data from ScaleKit structure: data.event
            if isinstance(response_dict, dict) and 'data' in response_dict:
                if 'event' in response_dict['data']:
                    event_data = response_dict['data']['event']
                    logger.debug(f"Event created successfully with ID: {event_data.get('id', 'Unknown')}")
                    
                    return {
                        "success": True,
                        "event": event_data,
                        "message": f"Successfully created calendar event: {summary}"
                    }
            
            return {
                "success": True,
                "event": response_dict,
                "message": f"Successfully created calendar event: {summary}"
            }
            
        except Exception as e:
            logger.error(f"Failed to create calendar event for user {self.user_id}: {str(e)}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to create calendar event: {str(e)}",
                "status": "error"
            }
    
    def get_tools(self) -> list:
        """Get Google Calendar function specifications for OpenAI"""
        # Check status dynamically instead of relying on is_enabled flag
        status = self.check_status()
        if not status.get('enabled', False):
            return []
        
        return [
            {
                            "name": "GOOGLECALENDAR_FETCH_EVENTS",
                            "description": "Retrieve calendar events from Google Calendar with detailed information including title, description, start/end times, attendees, and conference data. CRITICAL: When user asks for events for a specific date (today, tomorrow, or specific date like '27 August 2025'), you MUST calculate the correct UTC time range accounting for the user's local timezone. IMPORTANT: User is in PDT (UTC-8), so for 'August 28, 2025' set time_min to '2025-08-28T08:00:00Z' (00:00 PDT = 08:00 UTC) and time_max to '2025-08-29T08:00:00Z'. This ensures you get events for the user's local date, not UTC date. NOTE: All API times are in UTC (Z suffix), but frontend displays in local timezone. Requires an active Google Calendar connection through Google OAuth.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "max_results": {
                                        "type": "integer",
                                        "description": "Maximum number of events to retrieve (default: 10, max: 50)",
                                        "minimum": 1,
                                        "maximum": 50
                                    },
                                    "query": {
                                        "type": "string",
                                        "description": "Search query to filter events (e.g., 'meeting', 'zoom', 'team')"
                                    },
                                    "time_min": {
                                        "type": "string",
                                        "description": "CRITICAL: Start time for filtering events (ISO 8601 format, UTC). For date-specific queries, account for user's PDT timezone (UTC-8). For 'August 28, 2025' set to '2025-08-28T08:00:00Z' (00:00 PDT = 08:00 UTC). DO NOT leave empty for date queries."
                                    },
                                    "time_max": {
                                        "type": "string",
                                        "description": "CRITICAL: End time for filtering events (ISO 8601 format, UTC). For date-specific queries, account for user's PDT timezone (UTC-8). For 'August 28, 2025' set to '2025-08-29T08:00:00Z' (00:00 PDT = 08:00 UTC). DO NOT leave empty for date queries."
                                    }
                                },
                                "required": []
                            }
                        },
                        {
                            "name": "GOOGLECALENDAR_CREATE_EVENT",
                            "description": "Create a new calendar event in Google Calendar. CRITICAL: When user provides a time in local timezone (PDT), you MUST convert it to UTC before setting start_datetime. IMPORTANT: User is in PDT (UTC-8), so if they say '9:00 AM tomorrow', convert to '2025-08-28T17:00:00Z' (9:00 AM PDT = 5:00 PM UTC). Always set timezone to 'UTC' in tool_input. Requires an active Google Calendar connection through Google OAuth.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "summary": {
                                        "type": "string",
                                        "description": "Event title/summary (required)"
                                    },
                                    "start_datetime": {
                                        "type": "string",
                                        "description": "CRITICAL: Start time in UTC (ISO 8601 format with Z suffix). Convert user's local time to UTC. If user says '9:00 AM tomorrow PDT', set to '2025-08-28T17:00:00Z' (9:00 AM PDT = 5:00 PM UTC)."
                                    },
                                    "event_duration_minutes": {
                                        "type": "integer",
                                        "description": "Event duration in minutes (default: 30)",
                                        "minimum": 15,
                                        "maximum": 1440
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "Event description"
                                    },
                                    "location": {
                                        "type": "string",
                                        "description": "Event location"
                                    },
                                    "attendees_emails": {
                                        "type": "string",
                                        "description": "Comma-separated list of attendee email addresses"
                                    },
                                    "calendar_id": {
                                        "type": "string",
                                        "description": "Calendar ID (default: 'primary')"
                                    }
                                },
                                "required": ["summary", "start_datetime"]
                            }
                        }
                    ]
