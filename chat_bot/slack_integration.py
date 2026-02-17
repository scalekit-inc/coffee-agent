from typing import Dict, Any
import logging
from utils import convert_scalekit_response
from scalekit.common.exceptions import ScalekitNotFoundException, ScalekitBadRequestException
from scalekit_client import get_connect

logger = logging.getLogger(__name__)


class SlackIntegration:
    def __init__(self, user_id="default_user"):
        # Use shared ScaleKit client instead of creating a new one
        self.connect = get_connect()
        self.is_enabled = False
        self.user_id = user_id
    
    def enable(self) -> Dict[str, Any]:
        """Enable Slack integration and get authorization link if needed"""
        try:
            response = self.connect.get_connected_account(
                connection_name="slack-agent",
                identifier=self.user_id
            )
            
            if response.connected_account.status == "ACTIVE":
                self.is_enabled = True
                return {"success": True, "message": "Slack is already connected!", "status": "connected"}
            else:
                link_response = self.connect.get_authorization_link(
                    connection_name="slack-agent",
                    identifier=self.user_id
                )
                return {"success": True, "auth_link": link_response.link, "status": "needs_auth"}
                
        except Exception as e:
            logger.info(f"Slack account check failed for user {self.user_id}, getting auth link: {str(e)}")
            try:
                link_response = self.connect.get_authorization_link(
                    connection_name="slack-agent",
                    identifier=self.user_id
                )
                return {"success": True, "auth_link": link_response.link, "status": "needs_auth"}
            except Exception as link_error:
                logger.error(f"Failed to get Slack authorization link for user {self.user_id}: {str(link_error)}", exc_info=True)
                return {"success": False, "message": f"Failed to get authorization link: {str(link_error)}", "status": "error"}
    
    def check_status(self) -> Dict[str, Any]:
        """Check current Slack connection status"""
        try:
            response = self.connect.get_connected_account(
                connection_name="slack-agent",
                identifier=self.user_id
            )
            
            if response.connected_account.status == "ACTIVE":
                self.is_enabled = True
                return {"success": True, "enabled": True, "status": "connected"}
            else:
                self.is_enabled = False
                return {"success": True, "enabled": False, "status": response.connected_account.status}
                
        except ScalekitNotFoundException:
            # Expected when Slack is not configured or user hasn't connected yet
            logger.debug(f"Slack connection not found for user {self.user_id} (this is expected if Slack is not configured or not connected)")
            self.is_enabled = False
            return {"success": True, "enabled": False, "status": "not_connected"}
        except Exception as e:
            logger.warning(f"Failed to check Slack status for user {self.user_id}: {str(e)}", exc_info=True)
            self.is_enabled = False
            return {"success": False, "enabled": False, "status": "error"}
    
    def send_message(self, channel: str, text: str, thread_ts: str = "") -> Dict[str, Any]:
        """Send a message to a Slack channel or direct message"""
        if not self.is_enabled:
            return {"success": False, "message": "Slack integration is not enabled."}
        
        try:
            tool_input = {
                "channel": channel,
                "text": text,
            }
            
            if thread_ts:
                tool_input["thread_ts"] = thread_ts
            
            response = self.connect.execute_tool(
                tool_name="slack_send_message",
                identifier=self.user_id,
                tool_input=tool_input
            )
            
            # Convert response to dict
            response_dict = convert_scalekit_response(response)
            
            return {
                "success": True,
                "message": "Message sent successfully",
                "data": response_dict
            }
            
        except ScalekitBadRequestException as e:
            err_msg = str(e)
            if "failed to get tool" in err_msg or "RESOURCE_NOT_FOUND" in err_msg:
                logger.warning(f"Slack tool not available in ScaleKit for user {self.user_id}: {err_msg}")
                return {
                    "success": False,
                    "message": "Slack tools are not configured in your ScaleKit environment. Add the Slack connection and tools in the ScaleKit dashboard for this environment."
                }
            logger.error(f"Failed to send message for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to send message: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to send message for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to send message: {str(e)}"}
    
    def list_channels(self, exclude_archived: bool = True, max_results: int = 100) -> Dict[str, Any]:
        """List all channels in the Slack workspace"""
        if not self.is_enabled:
            return {"success": False, "message": "Slack integration is not enabled."}
        
        try:
            tool_input = {
                "exclude_archived": exclude_archived,
                "limit": min(max_results, 1000),
                "types": "public_channel,private_channel"
            }
            
            response = self.connect.execute_tool(
                tool_name="slack_list_channels",
                identifier=self.user_id,
                tool_input=tool_input
            )
            
            # Convert response to dict
            response_dict = convert_scalekit_response(response)
            
            # Extract channels from ScaleKit structure
            channels_list = []
            if isinstance(response_dict, dict) and 'data' in response_dict:
                if 'channels' in response_dict['data']:
                    channels_list = response_dict['data']['channels']
            
            # Process channels to extract key information
            if channels_list:
                processed_channels = []
                for channel in channels_list:
                    processed_channel = {
                        'id': channel.get('id'),
                        'name': channel.get('name'),
                        'is_private': channel.get('is_private', False),
                        'is_archived': channel.get('is_archived', False),
                        'num_members': channel.get('num_members', 0),
                        'topic': channel.get('topic', {}).get('value', ''),
                        'purpose': channel.get('purpose', {}).get('value', '')
                    }
                    processed_channels.append(processed_channel)
                
                return {
                    "success": True,
                    "channels": processed_channels,
                    "message": f"Successfully fetched {len(processed_channels)} channels"
                }
            
            return {
                "success": True,
                "channels": channels_list if channels_list else response_dict,
                "message": f"Successfully fetched {len(channels_list) if channels_list else 0} channels"
            }
            
        except ScalekitBadRequestException as e:
            err_msg = str(e)
            if "failed to get tool" in err_msg or "RESOURCE_NOT_FOUND" in err_msg:
                logger.warning(f"Slack tool not available in ScaleKit for user {self.user_id}: {err_msg}")
                return {
                    "success": False,
                    "message": "Slack tools are not configured in your ScaleKit environment. Add the Slack connection and tools in the ScaleKit dashboard for this environment."
                }
            logger.error(f"Failed to list channels for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to list channels: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to list channels for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to list channels: {str(e)}"}
    
    def fetch_conversation_history(self, channel: str, max_results: int = 100) -> Dict[str, Any]:
        """Fetch conversation history from a Slack channel or DM"""
        if not self.is_enabled:
            return {"success": False, "message": "Slack integration is not enabled."}
        
        try:
            tool_input = {
                "channel": channel,
                "limit": min(max_results, 1000)
            }
            
            response = self.connect.execute_tool(
                tool_name="slack_fetch_conversation_history",
                identifier=self.user_id,
                tool_input=tool_input
            )
            
            # Convert response to dict
            response_dict = convert_scalekit_response(response)
            
            # Extract messages from ScaleKit structure
            messages_list = []
            if isinstance(response_dict, dict) and 'data' in response_dict:
                if 'messages' in response_dict['data']:
                    messages_list = response_dict['data']['messages']
            
            # Process messages to extract key information
            if messages_list:
                processed_messages = []
                for message in messages_list:
                    processed_message = {
                        'type': message.get('type'),
                        'user': message.get('user'),
                        'text': message.get('text', ''),
                        'ts': message.get('ts'),
                        'thread_ts': message.get('thread_ts', ''),
                        'reply_count': message.get('reply_count', 0)
                    }
                    processed_messages.append(processed_message)
                
                return {
                    "success": True,
                    "messages": processed_messages,
                    "message": f"Successfully fetched {len(processed_messages)} messages"
                }
            
            return {
                "success": True,
                "messages": messages_list if messages_list else response_dict,
                "message": f"Successfully fetched {len(messages_list) if messages_list else 0} messages"
            }
            
        except ScalekitBadRequestException as e:
            err_msg = str(e)
            if "failed to get tool" in err_msg or "RESOURCE_NOT_FOUND" in err_msg:
                logger.warning(f"Slack tool not available in ScaleKit for user {self.user_id}: {err_msg}")
                return {
                    "success": False,
                    "message": "Slack tools are not configured in your ScaleKit environment. Add the Slack connection and tools in the ScaleKit dashboard for this environment."
                }
            logger.error(f"Failed to fetch conversation history for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to fetch conversation history: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to fetch conversation history for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to fetch conversation history: {str(e)}"}
    
    def create_channel(self, name: str, is_private: bool = False) -> Dict[str, Any]:
        """Create a new Slack channel"""
        if not self.is_enabled:
            return {"success": False, "message": "Slack integration is not enabled."}
        
        try:
            tool_input = {
                "name": name,
                "is_private": is_private
            }
            
            response = self.connect.execute_tool(
                tool_name="slack_create_channel",
                identifier=self.user_id,
                tool_input=tool_input
            )
            
            # Convert response to dict
            response_dict = convert_scalekit_response(response)
            
            # Extract channel data from ScaleKit structure
            if isinstance(response_dict, dict) and 'data' in response_dict:
                if 'channel' in response_dict['data']:
                    channel_data = response_dict['data']['channel']
                    logger.debug(f"Channel created successfully: {channel_data.get('name', 'Unknown')}")
                    
                    return {
                        "success": True,
                        "channel": channel_data,
                        "message": f"Successfully created channel: {name}"
                    }
            
            return {
                "success": True,
                "channel": response_dict,
                "message": f"Successfully created channel: {name}"
            }
            
        except ScalekitBadRequestException as e:
            err_msg = str(e)
            if "failed to get tool" in err_msg or "RESOURCE_NOT_FOUND" in err_msg:
                logger.warning(f"Slack tool not available in ScaleKit for user {self.user_id}: {err_msg}")
                return {
                    "success": False,
                    "message": "Slack tools are not configured in your ScaleKit environment. Add the Slack connection and tools in the ScaleKit dashboard for this environment."
                }
            logger.error(f"Failed to create channel for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to create channel: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to create channel for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to create channel: {str(e)}"}
    
    def list_users(self, max_results: int = 100) -> Dict[str, Any]:
        """List all users in the Slack workspace"""
        if not self.is_enabled:
            return {"success": False, "message": "Slack integration is not enabled."}
        
        try:
            tool_input = {
                "limit": min(max_results, 1000)
            }
            
            response = self.connect.execute_tool(
                tool_name="slack_list_users",
                identifier=self.user_id,
                tool_input=tool_input
            )
            
            # Convert response to dict
            response_dict = convert_scalekit_response(response)
            
            # Extract users from ScaleKit structure
            users_list = []
            if isinstance(response_dict, dict) and 'data' in response_dict:
                if 'members' in response_dict['data']:
                    users_list = response_dict['data']['members']
            
            # Process users to extract key information
            if users_list:
                processed_users = []
                for user in users_list:
                    processed_user = {
                        'id': user.get('id'),
                        'name': user.get('name'),
                        'real_name': user.get('real_name', ''),
                        'is_bot': user.get('is_bot', False),
                        'deleted': user.get('deleted', False),
                        'profile': {
                            'email': user.get('profile', {}).get('email', ''),
                            'display_name': user.get('profile', {}).get('display_name', ''),
                            'status_text': user.get('profile', {}).get('status_text', '')
                        }
                    }
                    processed_users.append(processed_user)
                
                return {
                    "success": True,
                    "users": processed_users,
                    "message": f"Successfully fetched {len(processed_users)} users"
                }
            
            return {
                "success": True,
                "users": users_list if users_list else response_dict,
                "message": f"Successfully fetched {len(users_list) if users_list else 0} users"
            }
            
        except ScalekitBadRequestException as e:
            err_msg = str(e)
            if "failed to get tool" in err_msg or "RESOURCE_NOT_FOUND" in err_msg:
                logger.warning(f"Slack tool not available in ScaleKit for user {self.user_id}: {err_msg}")
                return {
                    "success": False,
                    "message": "Slack tools are not configured in your ScaleKit environment. Add the Slack connection and tools in the ScaleKit dashboard for this environment."
                }
            logger.error(f"Failed to list users for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to list users: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to list users for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to list users: {str(e)}"}
    
    def get_tools(self) -> list:
        """Get Slack function specifications for OpenAI"""
        # Check status dynamically instead of relying on is_enabled flag
        status = self.check_status()
        if not status.get('enabled', False):
            return []
        
        return [
            {
                "name": "SLACK_SEND_MESSAGE",
                "description": "Send a message to a Slack channel or direct message. Can be used to send messages to channels (use #channel-name or channel ID) or direct messages (use user ID).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel": {
                            "type": "string",
                            "description": "Channel ID, channel name (#general), or user ID for DM"
                        },
                        "text": {
                            "type": "string",
                            "description": "Message text content to send"
                        },
                        "thread_ts": {
                            "type": "string",
                            "description": "Optional: Timestamp of parent message to reply in thread"
                        }
                    },
                    "required": ["channel", "text"]
                }
            },
            {
                "name": "SLACK_LIST_CHANNELS",
                "description": "List all public and private channels in the Slack workspace that the user has access to. Shows channel names, member counts, topics, and purposes.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "exclude_archived": {
                            "type": "boolean",
                            "description": "Exclude archived channels from the list (default: true)"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of channels to retrieve (default: 100, max: 1000)",
                            "minimum": 1,
                            "maximum": 1000
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "SLACK_FETCH_CONVERSATION_HISTORY",
                "description": "Fetch conversation history and messages from a Slack channel or direct message. Shows recent messages including user, text, and timestamp.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "channel": {
                            "type": "string",
                            "description": "Channel ID, channel name (#general), or user ID for DM"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of messages to retrieve (default: 100, max: 1000)",
                            "minimum": 1,
                            "maximum": 1000
                        }
                    },
                    "required": ["channel"]
                }
            },
            {
                "name": "SLACK_CREATE_CHANNEL",
                "description": "Create a new public or private channel in the Slack workspace. Returns the newly created channel information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the channel to create (without # prefix, lowercase, no spaces)"
                        },
                        "is_private": {
                            "type": "boolean",
                            "description": "Create a private channel instead of public (default: false)"
                        }
                    },
                    "required": ["name"]
                }
            },
            {
                "name": "SLACK_LIST_USERS",
                "description": "List all users in the Slack workspace, including their names, email addresses, and status information.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of users to retrieve (default: 100, max: 1000)",
                            "minimum": 1,
                            "maximum": 1000
                        }
                    },
                    "required": []
                }
            }
        ]

# Global instance
slack_integration = SlackIntegration()
