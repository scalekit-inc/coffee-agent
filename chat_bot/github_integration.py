from typing import Dict, Any
import logging
from utils import convert_scalekit_response
from scalekit.common.exceptions import ScalekitNotFoundException, ScalekitBadRequestException
from scalekit_client import get_connect

logger = logging.getLogger(__name__)


def _parse_owner_repo(repository: str) -> tuple:
    """Parse 'owner/repo' into (owner, repo). Falls back to (repository, '') if no slash."""
    if "/" in repository:
        parts = repository.split("/", 1)
        return (parts[0].strip(), parts[1].strip())
    return (repository.strip(), "")


class GitHubIntegration:
    def __init__(self, user_id="default_user"):
        # Use shared ScaleKit client instead of creating a new one
        self.connect = get_connect()
        self.is_enabled = False
        self.user_id = user_id
    
    def enable(self) -> Dict[str, Any]:
        """Enable GitHub integration and get authorization link if needed"""
        try:
            response = self.connect.get_connected_account(
                connection_name="github-agent",
                identifier=self.user_id
            )
            
            if response.connected_account.status == "ACTIVE":
                self.is_enabled = True
                return {"success": True, "message": "GitHub is already connected!", "status": "connected"}
            else:
                link_response = self.connect.get_authorization_link(
                    connection_name="github-agent",
                    identifier=self.user_id
                )
                return {"success": True, "auth_link": link_response.link, "status": "needs_auth"}
                
        except Exception as e:
            logger.info(f"GitHub account check failed for user {self.user_id}, getting auth link: {str(e)}")
            try:
                link_response = self.connect.get_authorization_link(
                    connection_name="github-agent",
                    identifier=self.user_id
                )
                return {"success": True, "auth_link": link_response.link, "status": "needs_auth"}
            except Exception as link_error:
                logger.error(f"Failed to get GitHub authorization link for user {self.user_id}: {str(link_error)}", exc_info=True)
                return {"success": False, "message": f"Failed to get authorization link: {str(link_error)}", "status": "error"}
    
    def check_status(self) -> Dict[str, Any]:
        """Check current GitHub connection status"""
        try:
            response = self.connect.get_connected_account(
                connection_name="github-agent",
                identifier=self.user_id
            )
            
            if response.connected_account.status == "ACTIVE":
                self.is_enabled = True
                return {"success": True, "enabled": True, "status": "connected"}
            else:
                self.is_enabled = False
                return {"success": True, "enabled": False, "status": response.connected_account.status}
                
        except ScalekitNotFoundException:
            # Expected when GitHub is not configured or user hasn't connected yet
            logger.debug(f"GitHub connection not found for user {self.user_id} (this is expected if GitHub is not configured or not connected)")
            self.is_enabled = False
            return {"success": True, "enabled": False, "status": "not_connected"}
        except Exception as e:
            logger.warning(f"Failed to check GitHub status for user {self.user_id}: {str(e)}", exc_info=True)
            self.is_enabled = False
            return {"success": False, "enabled": False, "status": "error"}
    
    def list_repositories(self, max_results: int = 10, type: str = "owner") -> Dict[str, Any]:
        """List GitHub repositories for the authenticated user"""
        if not self.is_enabled:
            return {"success": False, "message": "GitHub integration is not enabled."}
        
        try:
            # ScaleKit: github_user_repos_list — direction, page, per_page, sort, type
            tool_input = {
                "type": type,  # all, owner, public, private, member
                "per_page": min(max_results, 100),
                "page": 1,
                "sort": "updated",  # created, updated, pushed, full_name
                "direction": "desc",  # asc, desc
            }
            
            response = self.connect.execute_tool(
                tool_name="github_user_repos_list",
                identifier=self.user_id,
                tool_input=tool_input
            )
            
            # Convert response to dict
            response_dict = convert_scalekit_response(response)
            
            # Extract repositories from ScaleKit structure
            repos_list = []
            if isinstance(response_dict, dict) and 'data' in response_dict:
                if 'repositories' in response_dict['data']:
                    repos_list = response_dict['data']['repositories']
            
            # Process repositories to extract key information
            if repos_list:
                processed_repos = []
                for repo in repos_list:
                    processed_repo = {
                        'id': repo.get('id'),
                        'name': repo.get('name'),
                        'full_name': repo.get('full_name'),
                        'description': repo.get('description', ''),
                        'private': repo.get('private', False),
                        'url': repo.get('html_url', ''),
                        'language': repo.get('language', ''),
                        'stars': repo.get('stargazers_count', 0),
                        'forks': repo.get('forks_count', 0),
                        'open_issues': repo.get('open_issues_count', 0),
                        'created_at': repo.get('created_at', ''),
                        'updated_at': repo.get('updated_at', '')
                    }
                    processed_repos.append(processed_repo)
                
                return {
                    "success": True,
                    "repositories": processed_repos,
                    "message": f"Successfully fetched {len(processed_repos)} repositories"
                }
            
            return {
                "success": True,
                "repositories": repos_list if repos_list else response_dict,
                "message": f"Successfully fetched {len(repos_list) if repos_list else 0} repositories"
            }
            
        except ScalekitBadRequestException as e:
            err_msg = str(e)
            if "failed to get tool" in err_msg or "RESOURCE_NOT_FOUND" in err_msg:
                logger.warning(f"GitHub tool not available in ScaleKit for user {self.user_id}: {err_msg}")
                return {
                    "success": False,
                    "message": "GitHub tools are not configured in your ScaleKit environment. Add the GitHub connection and tools in the ScaleKit dashboard for this environment."
                }
            logger.error(f"Failed to list repositories for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to list repositories: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to list repositories for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to list repositories: {str(e)}"}
    
    def list_issues(self, repository: str, state: str = "open", max_results: int = 10) -> Dict[str, Any]:
        """List issues for a GitHub repository. repository should be 'owner/repo'."""
        if not self.is_enabled:
            return {"success": False, "message": "GitHub integration is not enabled."}
        
        owner, repo = _parse_owner_repo(repository)
        if not repo:
            return {"success": False, "message": "repository must be in 'owner/repo' format (e.g. octocat/Hello-World)."}
        
        try:
            # ScaleKit: github_issues_list — owner, repo, state, sort, direction, per_page, page, etc.
            tool_input = {
                "owner": owner,
                "repo": repo,
                "state": state,  # open, closed, all
                "per_page": min(max_results, 100),
                "page": 1,
                "sort": "created",  # created, updated, comments
                "direction": "desc",  # asc, desc
            }
            
            response = self.connect.execute_tool(
                tool_name="github_issues_list",
                identifier=self.user_id,
                tool_input=tool_input
            )
            
            # Convert response to dict
            response_dict = convert_scalekit_response(response)
            
            # Extract issues from ScaleKit structure
            issues_list = []
            if isinstance(response_dict, dict) and 'data' in response_dict:
                if 'issues' in response_dict['data']:
                    issues_list = response_dict['data']['issues']
            
            # Process issues to extract key information
            if issues_list:
                processed_issues = []
                for issue in issues_list:
                    processed_issue = {
                        'id': issue.get('id'),
                        'number': issue.get('number'),
                        'title': issue.get('title'),
                        'body': issue.get('body', ''),
                        'state': issue.get('state'),
                        'url': issue.get('html_url', ''),
                        'user': issue.get('user', {}).get('login', 'Unknown'),
                        'labels': [label.get('name') for label in issue.get('labels', [])],
                        'created_at': issue.get('created_at', ''),
                        'updated_at': issue.get('updated_at', ''),
                        'comments': issue.get('comments', 0)
                    }
                    processed_issues.append(processed_issue)
                
                return {
                    "success": True,
                    "issues": processed_issues,
                    "message": f"Successfully fetched {len(processed_issues)} issues"
                }
            
            return {
                "success": True,
                "issues": issues_list if issues_list else response_dict,
                "message": f"Successfully fetched {len(issues_list) if issues_list else 0} issues"
            }
            
        except ScalekitBadRequestException as e:
            err_msg = str(e)
            if "failed to get tool" in err_msg or "RESOURCE_NOT_FOUND" in err_msg:
                logger.warning(f"GitHub tool not available in ScaleKit for user {self.user_id}: {err_msg}")
                return {
                    "success": False,
                    "message": "GitHub tools are not configured in your ScaleKit environment. Add the GitHub connection and tools in the ScaleKit dashboard for this environment."
                }
            logger.error(f"Failed to list issues for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to list issues: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to list issues for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to list issues: {str(e)}"}
    
    def create_issue(self, repository: str, title: str, body: str = "", labels: str = "") -> Dict[str, Any]:
        """Create a new issue in a GitHub repository. repository should be 'owner/repo'."""
        if not self.is_enabled:
            return {"success": False, "message": "GitHub integration is not enabled."}
        
        owner, repo = _parse_owner_repo(repository)
        if not repo:
            return {"success": False, "message": "repository must be in 'owner/repo' format (e.g. octocat/Hello-World)."}
        
        try:
            # ScaleKit: github_issue_create — owner, repo, title, body, labels (array<string>), assignees, milestone, type
            label_list = [s.strip() for s in labels.split(",") if s.strip()] if labels else []
            tool_input = {
                "owner": owner,
                "repo": repo,
                "title": title,
                "body": body or "",
                "labels": label_list,
            }
            
            response = self.connect.execute_tool(
                tool_name="github_issue_create",
                identifier=self.user_id,
                tool_input=tool_input
            )
            
            # Convert response to dict
            response_dict = convert_scalekit_response(response)
            
            # Extract issue data from ScaleKit structure
            if isinstance(response_dict, dict) and 'data' in response_dict:
                if 'issue' in response_dict['data']:
                    issue_data = response_dict['data']['issue']
                    logger.debug(f"Issue created successfully with number: {issue_data.get('number', 'Unknown')}")
                    
                    return {
                        "success": True,
                        "issue": issue_data,
                        "message": f"Successfully created issue: {title}"
                    }
            
            return {
                "success": True,
                "issue": response_dict,
                "message": f"Successfully created issue: {title}"
            }
            
        except ScalekitBadRequestException as e:
            err_msg = str(e)
            if "failed to get tool" in err_msg or "RESOURCE_NOT_FOUND" in err_msg:
                logger.warning(f"GitHub tool not available in ScaleKit for user {self.user_id}: {err_msg}")
                return {
                    "success": False,
                    "message": "GitHub tools are not configured in your ScaleKit environment. Add the GitHub connection and tools in the ScaleKit dashboard for this environment."
                }
            logger.error(f"Failed to create issue for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to create issue: {str(e)}"}
        except Exception as e:
            logger.error(f"Failed to create issue for user {self.user_id}: {str(e)}", exc_info=True)
            return {"success": False, "message": f"Failed to create issue: {str(e)}"}
    
    def get_tools(self) -> list:
        """Get GitHub function specifications for OpenAI"""
        # Check status dynamically instead of relying on is_enabled flag
        status = self.check_status()
        if not status.get('enabled', False):
            return []
        
        return [
            {
                "name": "GITHUB_LIST_REPOSITORIES",
                "description": "List GitHub repositories for the authenticated user. Shows repository details including name, description, language, stars, and more.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of repositories to retrieve (default: 10, max: 100)",
                            "minimum": 1,
                            "maximum": 100
                        },
                        "type": {
                            "type": "string",
                            "description": "Type of repositories to list: 'owner' (default), 'all', 'public', 'private', or 'member'",
                            "enum": ["owner", "all", "public", "private", "member"]
                        }
                    },
                    "required": []
                }
            },
            {
                "name": "GITHUB_LIST_ISSUES",
                "description": "List issues from a specific GitHub repository. Shows issue details including title, body, state, labels, and more.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository": {
                            "type": "string",
                            "description": "Repository in 'owner/repo' format (e.g., 'octocat/Hello-World')"
                        },
                        "state": {
                            "type": "string",
                            "description": "Issue state filter: 'open' (default), 'closed', or 'all'",
                            "enum": ["open", "closed", "all"]
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of issues to retrieve (default: 10, max: 100)",
                            "minimum": 1,
                            "maximum": 100
                        }
                    },
                    "required": ["repository"]
                }
            },
            {
                "name": "GITHUB_CREATE_ISSUE",
                "description": "Create a new issue in a GitHub repository. Requires repository name, issue title, and optional body and labels.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "repository": {
                            "type": "string",
                            "description": "Repository in 'owner/repo' format (e.g., 'octocat/Hello-World')"
                        },
                        "title": {
                            "type": "string",
                            "description": "Issue title (required)"
                        },
                        "body": {
                            "type": "string",
                            "description": "Issue body/description (optional)"
                        },
                        "labels": {
                            "type": "string",
                            "description": "Comma-separated list of label names (optional, e.g., 'bug,enhancement')"
                        }
                    },
                    "required": ["repository", "title"]
                }
            }
        ]

# Global instance
github_integration = GitHubIntegration()
