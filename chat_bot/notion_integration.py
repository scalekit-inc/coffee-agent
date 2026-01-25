from typing import Dict, Any
import logging
from utils import convert_scalekit_response
from scalekit.common.exceptions import ScalekitNotFoundException
from scalekit_client import get_connect

logger = logging.getLogger(__name__)

class NotionIntegration:
    def __init__(self, user_id="default_user"):
        # Use shared ScaleKit client instead of creating a new one
        self.connect = get_connect()
        self.is_enabled = False
        self.user_id = user_id
    
    def enable(self) -> Dict[str, Any]:
        """Enable Notion integration and get authorization link if needed"""
        # First, try to check if account already exists and is active
        try:
            response = self.connect.get_connected_account(
                connection_name="NOTION",
                identifier=self.user_id
            )
            
            if response.connected_account.status == "ACTIVE":
                self.is_enabled = True
                return {"success": True, "message": "Notion is already connected!", "status": "connected"}
            else:
                # Account exists but not active, get auth link
                pass  # Fall through to get auth link
        except Exception as e:
            # Account doesn't exist or error getting account - this is OK, we'll get auth link
            error_msg = str(e)
            logger.debug(f"Notion account check - account may not exist yet (this is OK): {error_msg}")
        
        # Get authorization link (whether account exists or not)
        try:
            logger.debug(f"Attempting to get Notion auth link")
            logger.debug(f"connection_name='NOTION', identifier='{self.user_id}'")
            
            link_response = self.connect.get_authorization_link(
                connection_name="NOTION",
                identifier=self.user_id
            )
            return {"success": True, "auth_link": link_response.link, "status": "needs_auth"}
        except Exception as link_error:
            error_msg = str(link_error)
            error_type = type(link_error).__name__
            logger.debug(f"Error getting Notion auth link - Type: {error_type}, Message: {error_msg}")
            
            # Check if it's a NOT_FOUND error - this usually means Notion isn't configured in ScaleKit
            is_not_found = (
                "NOT_FOUND" in error_msg or 
                "not found" in error_msg.lower() or 
                "404" in error_msg or
                "INTERNAL_ERROR" in error_msg
            )
            
            if is_not_found:
                return {
                    "success": False,
                    "message": "Notion integration is not configured in your ScaleKit environment. Please ensure Notion connection is set up in the ScaleKit dashboard for your environment.",
                    "status": "error",
                    "error_code": "NOT_CONFIGURED"
                }
            else:
                # Extract more details if available
                error_details = error_msg
                if hasattr(link_error, 'details'):
                    error_details += f" | Details: {link_error.details}"
                if hasattr(link_error, 'code'):
                    error_details += f" | Code: {link_error.code}"
                
                return {
                    "success": False,
                    "message": f"Error getting Notion authorization link: {error_details}",
                    "status": "error"
                }
    
    def check_status(self) -> Dict[str, Any]:
        """Check current Notion connection status"""
        try:
            response = self.connect.get_connected_account(
                connection_name="NOTION",
                identifier=self.user_id
            )
            
            if response.connected_account.status == "ACTIVE":
                self.is_enabled = True
                return {"success": True, "enabled": True, "status": "connected"}
            else:
                self.is_enabled = False
                return {"success": True, "enabled": False, "status": response.connected_account.status}
                
        except ScalekitNotFoundException:
            # Expected when Notion is not configured or user hasn't connected yet
            logger.debug(f"Notion connection not found for user {self.user_id} (this is expected if Notion is not configured or not connected)")
            self.is_enabled = False
            return {"success": True, "enabled": False, "status": "not_connected"}
        except Exception as e:
            logger.warning(f"Failed to check Notion status for user {self.user_id}: {str(e)}", exc_info=True)
            self.is_enabled = False
            return {"success": False, "enabled": False, "status": "error"}
    
    def create_page(self, parent_page_id: str, title: str, content: str = "") -> Dict[str, Any]:
        """Create a new page in Notion"""
        if not self.is_enabled:
            return {"success": False, "message": "Notion integration is not enabled."}
        
        try:
            tool_input = {
                "parent_page_id": parent_page_id,
                "title": title,
                "content": content,
                "schema_version": "",
                "tool_version": ""
            }
            
            response = self.connect.execute_tool(
                tool_name="notion_create_page",
                identifier=self.user_id,
                tool_input=tool_input
            )
            
            # Convert response to dict
            response_dict = convert_scalekit_response(response)
            
            # Extract page data from ScaleKit structure
            page_data = None
            if isinstance(response_dict, dict) and 'data' in response_dict:
                page_data = response_dict['data']
            
            return {
                "success": True,
                "message": "Page created successfully",
                "data": page_data if page_data else response_dict
            }
            
        except Exception as e:
            logger.error(f"Failed to create Notion page for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to create Notion page: {str(e)}"}
    
    def search_pages(self, query: str = "", max_results: int = 10) -> Dict[str, Any]:
        """Search for pages in Notion"""
        if not self.is_enabled:
            return {"success": False, "message": "Notion integration is not enabled."}
        
        try:
            tool_input = {
                "query": query,
                "max_results": max_results,
                "schema_version": "",
                "tool_version": ""
            }
            
            response = self.connect.execute_tool(
                tool_name="notion_search_pages",
                identifier=self.user_id,
                tool_input=tool_input
            )
            
            # Convert response to dict
            response_dict = convert_scalekit_response(response)
            
            # Extract pages data from ScaleKit structure
            pages_data = None
            if isinstance(response_dict, dict) and 'data' in response_dict:
                pages_data = response_dict['data']
            
            return {
                "success": True,
                "message": "Pages retrieved successfully",
                "data": pages_data if pages_data else response_dict
            }
            
        except Exception as e:
            logger.error(f"Failed to search Notion pages for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to search Notion pages: {str(e)}"}
    
    def get_tools(self) -> list:
        """Get Notion function specifications for OpenAI"""
        # Check status dynamically instead of relying on is_enabled flag
        status = self.check_status()
        if not status.get('enabled', False):
            return []
        
        return [
            {
                "name": "NOTION_CREATE_PAGE",
                "description": "Create a new page in Notion. Requires a parent page ID where the new page will be created, a title, and optional content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "parent_page_id": {
                            "type": "string",
                            "description": "The ID of the parent page where the new page will be created"
                        },
                        "title": {
                            "type": "string",
                            "description": "The title of the new page"
                        },
                        "content": {
                            "type": "string",
                            "description": "Optional content/text for the page"
                        }
                    },
                    "required": ["parent_page_id", "title"]
                }
            },
            {
                "name": "NOTION_SEARCH_PAGES",
                "description": "Search for pages in Notion workspace. Can search by query string or retrieve recent pages.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Optional search query to filter pages by title or content"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 10)"
                        }
                    },
                    "required": []
                }
            }
        ]

# Global instance
notion_integration = NotionIntegration()
