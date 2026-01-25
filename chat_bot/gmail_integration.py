from typing import Dict, Any
import logging
from utils import convert_scalekit_response
from scalekit.common.exceptions import ScalekitNotFoundException
from scalekit_client import get_connect

logger = logging.getLogger(__name__)

class GmailIntegration:
    def __init__(self, user_id="default_user"):
        # Use shared ScaleKit client instead of creating a new one
        self.connect = get_connect()
        self.is_enabled = False
        self.user_id = user_id
    
    def enable(self) -> Dict[str, Any]:
        """Enable Gmail integration and get authorization link if needed"""
        try:
            response = self.connect.get_connected_account(
                connection_name="GMAIL",
                identifier=self.user_id
            )
            
            if response.connected_account.status == "ACTIVE":
                self.is_enabled = True
                return {"success": True, "message": "Gmail is already connected!", "status": "connected"}
            else:
                link_response = self.connect.get_authorization_link(
                    connection_name="GMAIL",
                    identifier=self.user_id
                )
                return {"success": True, "auth_link": link_response.link, "status": "needs_auth"}
                
        except Exception as e:
            logger.info(f"Gmail account check failed for user {self.user_id}, getting auth link: {str(e)}")
            try:
                link_response = self.connect.get_authorization_link(
                    connection_name="GMAIL",
                    identifier=self.user_id
                )
                return {"success": True, "auth_link": link_response.link, "status": "needs_auth"}
            except Exception as link_error:
                logger.error(f"Failed to get Gmail authorization link for user {self.user_id}: {str(link_error)}", exc_info=True)
                return {"success": False, "message": f"Failed to get authorization link: {str(link_error)}", "status": "error"}
    
    def check_status(self) -> Dict[str, Any]:
        """Check current Gmail connection status"""
        try:
            response = self.connect.get_connected_account(
                connection_name="GMAIL",
                identifier=self.user_id
            )
            
            if response.connected_account.status == "ACTIVE":
                self.is_enabled = True
                return {"success": True, "enabled": True, "status": "connected"}
            else:
                self.is_enabled = False
                return {"success": True, "enabled": False, "status": response.connected_account.status}
                
        except ScalekitNotFoundException:
            # Expected when Gmail is not configured or user hasn't connected yet
            logger.debug(f"Gmail connection not found for user {self.user_id} (this is expected if Gmail is not configured or not connected)")
            self.is_enabled = False
            return {"success": True, "enabled": False, "status": "not_connected"}
        except Exception as e:
            logger.warning(f"Failed to check Gmail status for user {self.user_id}: {str(e)}", exc_info=True)
            self.is_enabled = False
            return {"success": False, "enabled": False, "status": "error"}
    
    def fetch_emails(self, max_results: int = 5, query: str = "") -> Dict[str, Any]:
        """Fetch emails from Gmail"""
        if not self.is_enabled:
            return {"success": False, "message": "Gmail integration is not enabled."}
        
        try:
            tool_input = {
                "format": "metadata",
                "include_spam_trash": False,
                "label_ids": "",
                "max_results": str(max_results),
                "page_token": "",
                "query": query,
                "schema_version": "",
                "tool_version": ""
            }
            
            response = self.connect.execute_tool(
                tool_name="gmail_fetch_mails",
                identifier=self.user_id,
                tool_input=tool_input
            )
            
            # Convert response to dict
            response_dict = convert_scalekit_response(response)
            
            # Extract emails from ScaleKit structure: data.messages
            emails_list = []
            if isinstance(response_dict, dict) and 'data' in response_dict:
                if 'messages' in response_dict['data']:
                    emails_list = response_dict['data']['messages']
            
            # Process emails to extract key information for better AI understanding
            if emails_list:
                processed_emails = []
                for email in emails_list:
                    processed_email = {
                        'id': email.get('id'),
                        'snippet': email.get('snippet'),
                        'internalDate': email.get('internalDate'),
                        'subject': 'No Subject',
                        'sender': 'Unknown Sender',
                        'recipient': 'Unknown Recipient',
                        'date': 'Unknown Date'
                    }
                    
                    # Extract information from payload.headers
                    if email.get('payload') and email.get('payload', {}).get('headers'):
                        for header in email['payload']['headers']:
                            if header.get('name') == 'Subject':
                                processed_email['subject'] = header.get('value', 'No Subject')
                            elif header.get('name') == 'From':
                                processed_email['sender'] = header.get('value', 'Unknown Sender')
                            elif header.get('name') == 'To':
                                processed_email['recipient'] = header.get('value', 'Unknown Recipient')
                            elif header.get('name') == 'Date':
                                processed_email['date'] = header.get('value', 'Unknown Date')
                    
                    processed_emails.append(processed_email)
                
                return {
                    "success": True,
                    "emails": processed_emails,
                    "message": f"Successfully fetched {len(processed_emails)} emails"
                }
            
            return {
                "success": True,
                "emails": emails_list if emails_list else response_dict,
                "message": f"Successfully fetched {len(emails_list) if emails_list else max_results} emails"
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch emails for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to fetch emails: {str(e)}"}
    
    def get_tools(self) -> list:
        """Get Gmail function specifications for OpenAI"""
        # Check status dynamically instead of relying on is_enabled flag
        status = self.check_status()
        if not status.get('enabled', False):
            return []
        
        return [{
            "name": "GMAIL_FETCH_MAILS",
            "description": "Retrieve emails from Gmail inbox",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "integer",
                        "description": "Number of emails to retrieve (1-20)",
                        "minimum": 1,
                        "maximum": 20
                    },
                    "query": {
                        "type": "string",
                        "description": "Gmail search query (optional)"
                    }
                },
                "required": []
            }
        }]

# Global instance
gmail_integration = GmailIntegration()
