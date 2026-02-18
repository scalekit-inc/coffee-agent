from typing import Dict, Any
import logging
from utils import convert_scalekit_response
from scalekit.common.exceptions import ScalekitNotFoundException, ScalekitBadRequestException
from scalekit_client import get_connect

logger = logging.getLogger(__name__)


class HubSpotIntegration:
    def __init__(self, user_id="default_user"):
        # Use shared ScaleKit client instead of creating a new one
        self.connect = get_connect()
        self.is_enabled = False
        self.user_id = user_id
    
    def enable(self) -> Dict[str, Any]:
        """Enable HubSpot integration and get authorization link if needed"""
        try:
            response = self.connect.get_connected_account(
                connection_name="hubspot",
                identifier=self.user_id
            )
            
            if response.connected_account.status == "ACTIVE":
                self.is_enabled = True
                return {"success": True, "message": "HubSpot is already connected!", "status": "connected"}
            else:
                link_response = self.connect.get_authorization_link(
                    connection_name="hubspot",
                    identifier=self.user_id
                )
                return {"success": True, "auth_link": link_response.link, "status": "needs_auth"}
                
        except Exception as e:
            logger.info(f"HubSpot account check failed for user {self.user_id}, getting auth link: {str(e)}")
            try:
                link_response = self.connect.get_authorization_link(
                    connection_name="hubspot",
                    identifier=self.user_id
                )
                return {"success": True, "auth_link": link_response.link, "status": "needs_auth"}
            except Exception as link_error:
                logger.error(f"Failed to get HubSpot authorization link for user {self.user_id}: {str(link_error)}", exc_info=True)
                return {"success": False, "message": f"Failed to get authorization link: {str(link_error)}", "status": "error"}
    
    def check_status(self) -> Dict[str, Any]:
        """Check current HubSpot connection status"""
        try:
            response = self.connect.get_connected_account(
                connection_name="hubspot",
                identifier=self.user_id
            )
            
            if response.connected_account.status == "ACTIVE":
                self.is_enabled = True
                return {"success": True, "enabled": True, "status": "connected"}
            else:
                self.is_enabled = False
                return {"success": True, "enabled": False, "status": response.connected_account.status}
                
        except ScalekitNotFoundException:
            # Expected when HubSpot is not configured or user hasn't connected yet
            logger.debug(f"HubSpot connection not found for user {self.user_id} (this is expected if HubSpot is not configured or not connected)")
            self.is_enabled = False
            return {"success": True, "enabled": False, "status": "not_connected"}
        except Exception as e:
            logger.warning(f"Failed to check HubSpot status for user {self.user_id}: {str(e)}", exc_info=True)
            self.is_enabled = False
            return {"success": False, "enabled": False, "status": "error"}
    
    def list_contacts(self, max_results: int = 10, query: str = "") -> Dict[str, Any]:
        """List contacts from HubSpot CRM"""
        if not self.is_enabled:
            return {"success": False, "message": "HubSpot integration is not enabled."}
        
        try:
            tool_input = {
                "limit": min(max_results, 100),
                "properties": "firstname,lastname,email,company,phone,jobtitle,lifecyclestage"
            }
            
            response = self.connect.execute_tool(
                tool_name="hubspot_contacts_list",
                identifier=self.user_id,
                tool_input=tool_input
            )
            
            # Convert response to dict
            response_dict = convert_scalekit_response(response)
            
            # Extract contacts from ScaleKit structure
            contacts_list = []
            if isinstance(response_dict, dict) and 'data' in response_dict:
                if 'results' in response_dict['data']:
                    contacts_list = response_dict['data']['results']
            
            # Process contacts to extract key information
            if contacts_list:
                processed_contacts = []
                for contact in contacts_list:
                    properties = contact.get('properties', {})
                    processed_contact = {
                        'id': contact.get('id'),
                        'firstname': properties.get('firstname', ''),
                        'lastname': properties.get('lastname', ''),
                        'email': properties.get('email', ''),
                        'company': properties.get('company', ''),
                        'phone': properties.get('phone', ''),
                        'jobtitle': properties.get('jobtitle', ''),
                        'lifecyclestage': properties.get('lifecyclestage', '')
                    }
                    processed_contacts.append(processed_contact)
                
                return {
                    "success": True,
                    "contacts": processed_contacts,
                    "message": f"Successfully fetched {len(processed_contacts)} contacts"
                }
            
            return {
                "success": True,
                "contacts": contacts_list if contacts_list else response_dict,
                "message": f"Successfully fetched {len(contacts_list) if contacts_list else 0} contacts"
            }
            
        except ScalekitBadRequestException as e:
            err_msg = str(e)
            if "failed to get tool" in err_msg or "RESOURCE_NOT_FOUND" in err_msg:
                logger.warning(f"HubSpot tool not available in ScaleKit for user {self.user_id}: {err_msg}")
                return {
                    "success": False,
                    "message": "HubSpot tools are not configured in your ScaleKit environment. Add the HubSpot connection and tools in the ScaleKit dashboard for this environment."
                }
            logger.error(f"Failed to list contacts for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to list contacts: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to list contacts for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to list contacts: {str(e)}"}
    
    def create_contact(self, email: str, firstname: str = "", lastname: str = "", 
                      company: str = "", phone: str = "", jobtitle: str = "") -> Dict[str, Any]:
        """Create a new contact in HubSpot CRM"""
        if not self.is_enabled:
            return {"success": False, "message": "HubSpot integration is not enabled."}
        
        try:
            tool_input = {
                "email": email,
            }
            
            if firstname:
                tool_input["firstname"] = firstname
            if lastname:
                tool_input["lastname"] = lastname
            if company:
                tool_input["company"] = company
            if phone:
                tool_input["phone"] = phone
            if jobtitle:
                tool_input["jobtitle"] = jobtitle
            
            response = self.connect.execute_tool(
                tool_name="hubspot_contact_create",
                identifier=self.user_id,
                tool_input=tool_input
            )
            
            # Convert response to dict
            response_dict = convert_scalekit_response(response)
            
            return {
                "success": True,
                "message": f"Successfully created contact: {email}",
                "data": response_dict
            }
            
        except ScalekitBadRequestException as e:
            err_msg = str(e)
            if "failed to get tool" in err_msg or "RESOURCE_NOT_FOUND" in err_msg:
                logger.warning(f"HubSpot tool not available in ScaleKit for user {self.user_id}: {err_msg}")
                return {
                    "success": False,
                    "message": "HubSpot tools are not configured in your ScaleKit environment. Add the HubSpot connection and tools in the ScaleKit dashboard for this environment."
                }
            logger.error(f"Failed to create contact for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to create contact: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to create contact for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to create contact: {str(e)}"}
    
    def search_contacts(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """Search contacts in HubSpot CRM"""
        if not self.is_enabled:
            return {"success": False, "message": "HubSpot integration is not enabled."}
        
        try:
            tool_input = {
                "query": query,
                "limit": min(max_results, 100),
                "properties": "firstname,lastname,email,company,phone,jobtitle,lifecyclestage"
            }
            
            response = self.connect.execute_tool(
                tool_name="hubspot_contacts_search",
                identifier=self.user_id,
                tool_input=tool_input
            )
            
            # Convert response to dict
            response_dict = convert_scalekit_response(response)
            
            # Extract contacts from ScaleKit structure
            contacts_list = []
            if isinstance(response_dict, dict) and 'data' in response_dict:
                if 'results' in response_dict['data']:
                    contacts_list = response_dict['data']['results']
            
            # Process contacts to extract key information
            if contacts_list:
                processed_contacts = []
                for contact in contacts_list:
                    properties = contact.get('properties', {})
                    processed_contact = {
                        'id': contact.get('id'),
                        'firstname': properties.get('firstname', ''),
                        'lastname': properties.get('lastname', ''),
                        'email': properties.get('email', ''),
                        'company': properties.get('company', ''),
                        'phone': properties.get('phone', ''),
                        'jobtitle': properties.get('jobtitle', ''),
                        'lifecyclestage': properties.get('lifecyclestage', '')
                    }
                    processed_contacts.append(processed_contact)
                
                return {
                    "success": True,
                    "contacts": processed_contacts,
                    "message": f"Successfully found {len(processed_contacts)} contacts"
                }
            
            return {
                "success": True,
                "contacts": contacts_list if contacts_list else response_dict,
                "message": f"Successfully found {len(contacts_list) if contacts_list else 0} contacts"
            }
            
        except ScalekitBadRequestException as e:
            err_msg = str(e)
            if "failed to get tool" in err_msg or "RESOURCE_NOT_FOUND" in err_msg:
                logger.warning(f"HubSpot tool not available in ScaleKit for user {self.user_id}: {err_msg}")
                return {
                    "success": False,
                    "message": "HubSpot tools are not configured in your ScaleKit environment. Add the HubSpot connection and tools in the ScaleKit dashboard for this environment."
                }
            logger.error(f"Failed to search contacts for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to search contacts: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to search contacts for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to search contacts: {str(e)}"}
    
    def list_companies(self, max_results: int = 10) -> Dict[str, Any]:
        """List companies from HubSpot CRM"""
        if not self.is_enabled:
            return {"success": False, "message": "HubSpot integration is not enabled."}
        
        try:
            tool_input = {
                "limit": min(max_results, 100),
                "properties": "name,domain,industry,city,state,country,phone"
            }
            
            response = self.connect.execute_tool(
                tool_name="hubspot_companies_search",
                identifier=self.user_id,
                tool_input=tool_input
            )
            
            # Convert response to dict
            response_dict = convert_scalekit_response(response)
            
            # Extract companies from ScaleKit structure
            companies_list = []
            if isinstance(response_dict, dict) and 'data' in response_dict:
                if 'results' in response_dict['data']:
                    companies_list = response_dict['data']['results']
            
            # Process companies to extract key information
            if companies_list:
                processed_companies = []
                for company in companies_list:
                    properties = company.get('properties', {})
                    processed_company = {
                        'id': company.get('id'),
                        'name': properties.get('name', ''),
                        'domain': properties.get('domain', ''),
                        'industry': properties.get('industry', ''),
                        'city': properties.get('city', ''),
                        'state': properties.get('state', ''),
                        'country': properties.get('country', ''),
                        'phone': properties.get('phone', '')
                    }
                    processed_companies.append(processed_company)
                
                return {
                    "success": True,
                    "companies": processed_companies,
                    "message": f"Successfully fetched {len(processed_companies)} companies"
                }
            
            return {
                "success": True,
                "companies": companies_list if companies_list else response_dict,
                "message": f"Successfully fetched {len(companies_list) if companies_list else 0} companies"
            }
            
        except ScalekitBadRequestException as e:
            err_msg = str(e)
            if "failed to get tool" in err_msg or "RESOURCE_NOT_FOUND" in err_msg:
                logger.warning(f"HubSpot tool not available in ScaleKit for user {self.user_id}: {err_msg}")
                return {
                    "success": False,
                    "message": "HubSpot tools are not configured in your ScaleKit environment. Add the HubSpot connection and tools in the ScaleKit dashboard for this environment."
                }
            logger.error(f"Failed to list companies for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to list companies: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to list companies for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to list companies: {str(e)}"}
    
    def get_tools(self) -> list:
        """Get HubSpot function specifications for OpenAI"""
        # Check status dynamically instead of relying on is_enabled flag
        status = self.check_status()
        if not status.get('enabled', False):
            return []
        
        return [
            {
                "name": "HUBSPOT_LIST_CONTACTS",
                "description": "List contacts from HubSpot CRM. Shows contact details including name, email, company, phone, job title, and lifecycle stage.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of contacts to retrieve (default: 10, max: 100)",
                            "minimum": 1,
                            "maximum": 100
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "HUBSPOT_CREATE_CONTACT",
                "description": "Create a new contact in HubSpot CRM. Requires an email address. Optional fields include name, company, phone, and job title.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Email address of the contact (required)"
                        },
                        "firstname": {
                            "type": "string",
                            "description": "First name of the contact"
                        },
                        "lastname": {
                            "type": "string",
                            "description": "Last name of the contact"
                        },
                        "company": {
                            "type": "string",
                            "description": "Company name where the contact works"
                        },
                        "phone": {
                            "type": "string",
                            "description": "Phone number of the contact"
                        },
                        "jobtitle": {
                            "type": "string",
                            "description": "Job title of the contact"
                        }
                    },
                    "required": ["email"]
                }
            },
            {
                "name": "HUBSPOT_SEARCH_CONTACTS",
                "description": "Search for contacts in HubSpot CRM using a search query. Returns matching contacts with their details.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search term to find contacts (searches across name, email, company, etc.)"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of contacts to retrieve (default: 10, max: 100)",
                            "minimum": 1,
                            "maximum": 100
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "HUBSPOT_LIST_COMPANIES",
                "description": "List companies from HubSpot CRM. Shows company details including name, domain, industry, location, and phone.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of companies to retrieve (default: 10, max: 100)",
                            "minimum": 1,
                            "maximum": 100
                        }
                    },
                    "required": []
                }
            }
        ]

# Global instance
hubspot_integration = HubSpotIntegration()
