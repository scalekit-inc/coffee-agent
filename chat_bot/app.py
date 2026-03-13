from flask import Flask, request, jsonify, render_template, session, redirect
from flask_cors import CORS
import openai
import os
import secrets
from dotenv import load_dotenv
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from types import SimpleNamespace
from gmail_integration import GmailIntegration
from calendar_integration import CalendarIntegration
from notion_integration import NotionIntegration
from github_integration import GitHubIntegration
from slack_integration import SlackIntegration
from hubspot_integration import HubSpotIntegration
from config import (
    OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE, OPENAI_TIMEOUT_SEC,
    FUNCTION_GMAIL_FETCH_MAILS, FUNCTION_CALENDAR_FETCH_EVENTS,
    FUNCTION_CALENDAR_CREATE_EVENT, FUNCTION_NOTION_CREATE_PAGE, FUNCTION_NOTION_SEARCH_PAGES,
    FUNCTION_GITHUB_LIST_REPOSITORIES, FUNCTION_GITHUB_LIST_ISSUES, FUNCTION_GITHUB_CREATE_ISSUE,
    FUNCTION_SLACK_SEND_MESSAGE, FUNCTION_SLACK_LIST_CHANNELS, FUNCTION_SLACK_FETCH_CONVERSATION_HISTORY,
    FUNCTION_SLACK_CREATE_CHANNEL, FUNCTION_SLACK_LIST_USERS,
    FUNCTION_HUBSPOT_LIST_CONTACTS, FUNCTION_HUBSPOT_CREATE_CONTACT, FUNCTION_HUBSPOT_SEARCH_CONTACTS,
    FUNCTION_HUBSPOT_LIST_COMPANIES,
    USER_TIMEZONE, USER_TIMEZONE_OFFSET
)

# Load environment variables
load_dotenv()

# System Prompt for AI Assistant
SYSTEM_PROMPT = f"""You are an AI assistant with Gmail, Google Calendar, Notion, GitHub, Slack, and HubSpot integration.

CRITICAL - ACCURACY:
- Only claim you performed an action (e.g. created an issue, sent a Slack message, created a calendar event) if you actually called the corresponding tool and the tool result had "success": true. Never claim success for something you did not do via a tool call.
- If the user asks for an action that requires an integration (e.g. create a GitHub issue) but you do not have that tool available, say clearly that the integration is not connected and they need to connect it in the integrations settings. Do not invent or assume success.
- If you call a tool and the result has "success": false or an error message, report that to the user (e.g. "GitHub is not connected" or the actual error). Do not claim the action succeeded.

RESPONSE FORMAT:
- Emails: Brief summary, mention "emails displayed below". Use 'sender' field (From), not 'recipient' (To).
- Calendar events: Brief summary only (1-2 sentences), mention "events displayed below". Never list individual events.
- Notion pages: Brief summary, mention "pages displayed below" when showing search results.
- GitHub: Brief summary of repositories or issues, mention key details like names, states, and URLs.
- Slack: Brief summary of channels, messages, or users. Mention key details like channel names and message counts.
- HubSpot: Brief summary of contacts or companies. Mention key details like names, emails, and company information.

TIMEZONE ({USER_TIMEZONE}, {USER_TIMEZONE_OFFSET}):
- Fetching events: Convert user's date to UTC range. For date X, set time_min to start of X in UTC, time_max to start of next day in UTC.
- Creating events: Convert user's local time to UTC for start_datetime. Always set timezone='UTC' in tool_input.

NOTION:
- Creating pages: Requires parent_page_id. Confirm when page is created.
- Searching pages: Provide brief summary of results.

GITHUB:
- Listing repositories: Show key details like name, description, language, and stars.
- Listing issues: Show issue number, title, state, and labels.
- Creating issues: Confirm when issue is created with issue number and URL.

SLACK:
- Sending messages: Use channel name (#channel-name) or channel ID. Confirm when message is sent.
- Listing channels: Show channel names, member counts, and purposes.
- Fetching messages: Show recent messages with user and timestamp information.
- Creating channels: Confirm when channel is created with channel name.

HUBSPOT:
- Listing contacts: Show contact names, emails, companies, and job titles.
- Creating contacts: Confirm when contact is created with email address.
- Searching contacts: Show matching contacts with relevant details.
- Listing companies: Show company names, domains, industries, and locations."""

# Configure logging
# Support DEBUG level via LOG_LEVEL env var for Cloud Run debugging
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
CORS(app)

# Initialize OpenAI client with timeout
openai.api_key = os.getenv("OPENAI_API_KEY")
# Set timeout for OpenAI API calls
openai.api_requestor.REQUEST_TIMEOUT_SEC = OPENAI_TIMEOUT_SEC

@app.route('/')
def index():
    """Redirect to login page"""
    return render_template('login.html')

@app.route('/login')
def login():
    """Serve the login page"""
    return render_template('login.html')

@app.route('/chat')
def chat_page():
    """Serve the chat page (requires authentication)"""
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle login API request"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Basic validation
        if not email or not password:
            return jsonify({'success': False, 'message': 'All fields are required'})
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'})
        
        # Store user info in session
        session['user_email'] = email
        session['user_name'] = email.split('@')[0]
        
        return jsonify({
            'success': True, 
            'message': 'Login successful',
            'user': {'name': session['user_name'], 'email': session['user_email']}
        })
        
    except Exception as e:
        logger.error(f"Login failed: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'Login failed: {str(e)}'})

@app.route('/api/me')
def api_me():
    """Return current user from session (for chat page when user logged in via Google or email)."""
    email = session.get('user_email')
    name = session.get('user_name', (email or '').split('@')[0] if email else '')
    if not email:
        return jsonify({'authenticated': False}), 401
    return jsonify({
        'authenticated': True,
        'user': {'name': name, 'email': email}
    })


@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Handle logout API request"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})


def _scalekit_redirect_uri():
    """Build the redirect URI for ScaleKit OAuth (must match exactly in ScaleKit dashboard)."""
    base = request.url_root.rstrip('/')
    return f"{base}/api/scalekit/callback"


@app.route('/api/scalekit/authorize')
def scalekit_authorize():
    """Redirect to ScaleKit OAuth with provider=google for Sign in with Google."""
    try:
        from scalekit.common.scalekit import AuthorizationUrlOptions
        from scalekit_client import get_scalekit_client
    except ImportError as e:
        logger.error(f"ScaleKit import error: {e}", exc_info=True)
        return redirect('/login?error=config')
    provider = request.args.get('provider', 'google').strip().lower()
    if provider != 'google':
        return redirect('/login?error=unsupported_provider')
    state = secrets.token_urlsafe(24)
    session['scalekit_oauth_state'] = state
    redirect_uri = _scalekit_redirect_uri()
    options = AuthorizationUrlOptions()
    options.state = state
    options.provider = 'google'
    options.scopes = ['openid', 'profile', 'email', 'offline_access']
    client = get_scalekit_client()
    auth_url = client.get_authorization_url(redirect_uri, options)
    logger.debug(f"Redirecting to ScaleKit authorize: provider={provider}")
    return redirect(auth_url)


@app.route('/api/scalekit/callback')
def scalekit_callback():
    """Handle ScaleKit OAuth callback: exchange code for tokens, get email, log user in."""
    error = request.args.get('error')
    error_desc = request.args.get('error_description', '')
    if error:
        logger.warning(f"ScaleKit callback error: {error} - {error_desc}")
        return redirect(f'/login?error=auth_failed&message={error_desc}')
    code = request.args.get('code')
    state = request.args.get('state')
    if not code:
        return redirect('/login?error=missing_code')
    stored_state = session.pop('scalekit_oauth_state', None)
    if not state or state != stored_state:
        logger.warning("ScaleKit callback: invalid or missing state (CSRF)")
        return redirect('/login?error=invalid_state')
    try:
        from scalekit.common.scalekit import CodeAuthenticationOptions
        from scalekit_client import get_scalekit_client
    except ImportError as e:
        logger.error(f"ScaleKit import error: {e}", exc_info=True)
        return redirect('/login?error=config')
    redirect_uri = _scalekit_redirect_uri()
    try:
        client = get_scalekit_client()
        auth_result = client.authenticate_with_code(code, redirect_uri, CodeAuthenticationOptions())
    except Exception as e:
        logger.error(f"ScaleKit token exchange failed: {e}", exc_info=True)
        return redirect('/login?error=exchange_failed')
    user = auth_result.get('user') or {}
    email = (user.get('email') or '').strip()
    if not email:
        logger.warning("ScaleKit callback: no email in user object")
        return redirect('/login?error=no_email')
    session['user_email'] = email
    session['user_name'] = (user.get('name') or email.split('@')[0])
    logger.info(f"User logged in via ScaleKit Google: {email}")
    return redirect('/chat')


def get_user_integrations():
    """Get user-specific integration instances"""
    # Get user info from session (stored during login)
    user_email = session.get('user_email', 'default_user')
    user_name = session.get('user_name', 'default_user')
    
    # Use email as identifier, fallback to name, then default
    user_id = user_email if user_email and user_email != 'default_user' else (user_name if user_name and user_name != 'default_user' else 'default_user')
    
    logger.debug(f"Session data - user_email: {user_email}, user_name: {user_name}")
    logger.debug(f"Creating integrations with user_id: {user_id}")
    logger.debug(f"All session data: {dict(session)}")
    
    return (
        GmailIntegration(user_id=user_id),
        CalendarIntegration(user_id=user_id),
        NotionIntegration(user_id=user_id),
        GitHubIntegration(user_id=user_id),
        SlackIntegration(user_id=user_id),
        HubSpotIntegration(user_id=user_id)
    )

def get_openai_final_response(messages, function_name=""):
    """Get final response from OpenAI after function execution"""
    try:
        response = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=OPENAI_MAX_TOKENS,
            temperature=OPENAI_TEMPERATURE
        )
        return response, None
    except Exception as e:
        logger.error(f"OpenAI Error in final response after {function_name}: {str(e)}", exc_info=True)
        return None, f'Failed to get AI response: {str(e)}'

def execute_function_call(function_name, function_args, gmail_integration_instance, 
                          calendar_integration_instance, notion_integration_instance,
                          github_integration_instance, slack_integration_instance,
                          hubspot_integration_instance):
    """Execute a function call and return the result"""
    if function_name == FUNCTION_GMAIL_FETCH_MAILS:
        return gmail_integration_instance.fetch_emails(
            max_results=function_args.get("max_results", 5),
            query=function_args.get("query", "")
        )
    elif function_name == FUNCTION_CALENDAR_FETCH_EVENTS:
        return calendar_integration_instance.fetch_events(
            max_results=function_args.get("max_results", 10),
            query=function_args.get("query", ""),
            time_min=function_args.get("time_min", ""),
            time_max=function_args.get("time_max", ""),
            date=function_args.get("date", "")
        )
    elif function_name == FUNCTION_CALENDAR_CREATE_EVENT:
        return calendar_integration_instance.create_event(
            summary=function_args.get("summary", ""),
            start_datetime=function_args.get("start_datetime", ""),
            event_duration_minutes=function_args.get("event_duration_minutes", 30),
            description=function_args.get("description", ""),
            location=function_args.get("location", ""),
            attendees_emails=function_args.get("attendees_emails", ""),
            calendar_id=function_args.get("calendar_id", "primary")
        )
    elif function_name == FUNCTION_NOTION_CREATE_PAGE:
        return notion_integration_instance.create_page(
            parent_page_id=function_args.get("parent_page_id", ""),
            title=function_args.get("title", ""),
            content=function_args.get("content", "")
        )
    elif function_name == FUNCTION_NOTION_SEARCH_PAGES:
        return notion_integration_instance.search_pages(
            query=function_args.get("query", ""),
            max_results=function_args.get("max_results", 10)
        )
    elif function_name == FUNCTION_GITHUB_LIST_REPOSITORIES:
        return github_integration_instance.list_repositories(
            max_results=function_args.get("max_results", 10),
            type=function_args.get("type", "owner")
        )
    elif function_name == FUNCTION_GITHUB_LIST_ISSUES:
        return github_integration_instance.list_issues(
            repository=function_args.get("repository", ""),
            state=function_args.get("state", "open"),
            max_results=function_args.get("max_results", 10)
        )
    elif function_name == FUNCTION_GITHUB_CREATE_ISSUE:
        return github_integration_instance.create_issue(
            repository=function_args.get("repository", ""),
            title=function_args.get("title", ""),
            body=function_args.get("body", ""),
            labels=function_args.get("labels", "")
        )
    elif function_name == FUNCTION_SLACK_SEND_MESSAGE:
        return slack_integration_instance.send_message(
            channel=function_args.get("channel", ""),
            text=function_args.get("text", ""),
            thread_ts=function_args.get("thread_ts", "")
        )
    elif function_name == FUNCTION_SLACK_LIST_CHANNELS:
        return slack_integration_instance.list_channels(
            exclude_archived=function_args.get("exclude_archived", True),
            max_results=function_args.get("max_results", 100)
        )
    elif function_name == FUNCTION_SLACK_FETCH_CONVERSATION_HISTORY:
        return slack_integration_instance.fetch_conversation_history(
            channel=function_args.get("channel", ""),
            max_results=function_args.get("max_results", 100)
        )
    elif function_name == FUNCTION_SLACK_CREATE_CHANNEL:
        return slack_integration_instance.create_channel(
            name=function_args.get("name", ""),
            is_private=function_args.get("is_private", False)
        )
    elif function_name == FUNCTION_SLACK_LIST_USERS:
        return slack_integration_instance.list_users(
            max_results=function_args.get("max_results", 100)
        )
    elif function_name == FUNCTION_HUBSPOT_LIST_CONTACTS:
        return hubspot_integration_instance.list_contacts(
            max_results=function_args.get("max_results", 10)
        )
    elif function_name == FUNCTION_HUBSPOT_CREATE_CONTACT:
        return hubspot_integration_instance.create_contact(
            email=function_args.get("email", ""),
            firstname=function_args.get("firstname", ""),
            lastname=function_args.get("lastname", ""),
            company=function_args.get("company", ""),
            phone=function_args.get("phone", ""),
            jobtitle=function_args.get("jobtitle", "")
        )
    elif function_name == FUNCTION_HUBSPOT_SEARCH_CONTACTS:
        return hubspot_integration_instance.search_contacts(
            query=function_args.get("query", ""),
            max_results=function_args.get("max_results", 10)
        )
    elif function_name == FUNCTION_HUBSPOT_LIST_COMPANIES:
        return hubspot_integration_instance.list_companies(
            max_results=function_args.get("max_results", 10)
        )
    else:
        raise ValueError(f"Unknown function: {function_name}")

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages and return AI responses"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Create conversation context
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
        
        # Get user-specific integrations
        gmail_integration_instance, calendar_integration_instance, notion_integration_instance, github_integration_instance, slack_integration_instance, hubspot_integration_instance = get_user_integrations()
        
        # Get available tools based on integration status
        tools = []
        gmail_tools = gmail_integration_instance.get_tools()
        tools.extend(gmail_tools)
        logger.debug(f"Chat - user_id: {gmail_integration_instance.user_id}, Gmail tools available: {len(gmail_tools)}")
        
        calendar_tools = calendar_integration_instance.get_tools()
        tools.extend(calendar_tools)
        logger.debug(f"Chat - user_id: {calendar_integration_instance.user_id}, Calendar tools available: {len(calendar_tools)}")
        
        notion_tools = notion_integration_instance.get_tools()
        tools.extend(notion_tools)
        logger.debug(f"Chat - user_id: {notion_integration_instance.user_id}, Notion tools available: {len(notion_tools)}")
        
        github_tools = github_integration_instance.get_tools()
        tools.extend(github_tools)
        logger.debug(f"Chat - user_id: {github_integration_instance.user_id}, GitHub tools available: {len(github_tools)}")
        
        slack_tools = slack_integration_instance.get_tools()
        tools.extend(slack_tools)
        logger.debug(f"Chat - user_id: {slack_integration_instance.user_id}, Slack tools available: {len(slack_tools)}")
        
        hubspot_tools = hubspot_integration_instance.get_tools()
        tools.extend(hubspot_tools)
        logger.debug(f"Chat - user_id: {hubspot_integration_instance.user_id}, HubSpot tools available: {len(hubspot_tools)}")
        
        logger.debug(f"Chat - Total tools available: {len(tools)}")
        
        # Validate OpenAI API key before making calls
        if not openai.api_key or openai.api_key == "your_openai_api_key_here":
            return jsonify({
                'error': 'OpenAI API key is not configured. Please set OPENAI_API_KEY in your .env file.'
            }), 500
        
        # Get response from OpenAI
        if tools:
            # Use function/tool calling with multi-round tool use and parallel execution
            max_tool_rounds = 10
            tools_for_api = [{"type": "function", "function": t} for t in tools]
            try:
                for _ in range(max_tool_rounds):
                    response = openai.ChatCompletion.create(
                        model=OPENAI_MODEL,
                        messages=messages,
                        tools=tools_for_api,
                        tool_choice="auto",
                        max_completion_tokens=OPENAI_MAX_TOKENS,
                        temperature=OPENAI_TEMPERATURE
                    )
                    message = response.choices[0].message
                    # Prefer tool_calls; normalize legacy function_call to list
                    tool_calls = getattr(message, "tool_calls", None)
                    if not tool_calls and getattr(message, "function_call", None):
                        fc = message.function_call
                        tool_calls = [SimpleNamespace(id=getattr(fc, "id", "legacy_1"), function=SimpleNamespace(name=fc.name, arguments=fc.arguments))]
                    if not tool_calls:
                        break
                    # Append assistant message (serialize for API)
                    assistant_msg = {"role": "assistant", "content": message.content or ""}
                    assistant_msg["tool_calls"] = [
                        {"id": tc.id, "type": getattr(tc, "type", "function"), "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                        for tc in tool_calls
                    ]
                    messages.append(assistant_msg)
                    # Execute tool calls in parallel to reduce latency when multiple tools are requested
                    def run_one_tool(tc):
                        try:
                            function_args = json.loads(tc.function.arguments) if getattr(tc.function, "arguments", None) else {}
                        except json.JSONDecodeError:
                            function_args = {}
                        try:
                            result = execute_function_call(
                                tc.function.name,
                                function_args,
                                gmail_integration_instance,
                                calendar_integration_instance,
                                notion_integration_instance,
                                github_integration_instance,
                                slack_integration_instance,
                                hubspot_integration_instance
                            )
                            return (tc.id, json.dumps(result), None)
                        except Exception as e:
                            return (tc.id, None, e)
                    results_by_id = {}
                    with ThreadPoolExecutor(max_workers=min(len(tool_calls), 8)) as executor:
                        futures = {executor.submit(run_one_tool, tc): tc for tc in tool_calls}
                        for future in as_completed(futures):
                            tid, content, err = future.result()
                            if err:
                                logger.error(f"Error executing tool: {str(err)}", exc_info=True)
                                return jsonify({"error": f"Failed to execute tool: {str(err)}"}), 500
                            results_by_id[tid] = content
                    for tc in tool_calls:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": results_by_id[tc.id]
                        })
            except openai.error.AuthenticationError as e:
                logger.error(f"OpenAI Authentication Error: {str(e)}", exc_info=True)
                return jsonify({
                    'error': 'Invalid OpenAI API key. Please check your OPENAI_API_KEY in the .env file.'
                }), 500
            except openai.error.APIError as e:
                logger.error(f"OpenAI API Error: {str(e)}", exc_info=True)
                # Extract user-friendly error message
                error_msg = str(e)
                if "invalid_api_key" in error_msg or "Incorrect API key" in error_msg:
                    error_msg = "Invalid OpenAI API key. Please check your OPENAI_API_KEY in the .env file and ensure it's a valid key from https://platform.openai.com/api-keys"
                return jsonify({
                    'error': error_msg
                }), 500
            except Exception as e:
                logger.error(f"OpenAI Request Error: {str(e)}", exc_info=True)
                return jsonify({
                    'error': f'Failed to connect to OpenAI: {str(e)}'
                }), 500
            
            # Handle function calls if any (model may return text only — no function_call)
            message = response.choices[0].message
            function_call = getattr(message, "function_call", None)
            if function_call:
                function_name = function_call.name
                function_args = json.loads(function_call.arguments)
                
                # Execute the function call
                try:
                    function_result = execute_function_call(
                        function_name, 
                        function_args,
                        gmail_integration_instance,
                        calendar_integration_instance,
                        notion_integration_instance,
                        github_integration_instance,
                        slack_integration_instance,
                        hubspot_integration_instance
                    )
                except Exception as e:
                    logger.error(f"Error executing function {function_name}: {str(e)}", exc_info=True)
                    return jsonify({
                        'error': f'Failed to execute {function_name}: {str(e)}'
                    }), 500
                
                # Add function result to conversation
                messages.append(message)
                messages.append({
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(function_result)
                })
                
                # Get final response from OpenAI
                response, error = get_openai_final_response(messages, function_name)
                if error:
                    return jsonify({'error': error}), 500
        else:
            # No tools available, use regular chat
            try:
                response = openai.ChatCompletion.create(
                    model=OPENAI_MODEL,
                    messages=messages,
                    max_tokens=OPENAI_MAX_TOKENS,
                    temperature=OPENAI_TEMPERATURE
                )
            except openai.error.AuthenticationError as e:
                logger.error(f"OpenAI Authentication Error: {str(e)}", exc_info=True)
                return jsonify({
                    'error': 'Invalid OpenAI API key. Please check your OPENAI_API_KEY in the .env file.'
                }), 500
            except Exception as e:
                logger.error(f"OpenAI Error: {str(e)}", exc_info=True)
                return jsonify({
                    'error': f'Failed to connect to OpenAI: {str(e)}'
                }), 500
        
        ai_response = response.choices[0].message.content
        
        # Check if we have data from function calls
        email_data = None
        calendar_data = None
        for msg in messages:
            if msg.get("role") == "function" and msg.get("name") == FUNCTION_GMAIL_FETCH_MAILS:
                try:
                    email_data = json.loads(msg.get("content", "{}"))
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse email data from function response: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error parsing email data: {str(e)}", exc_info=True)
            elif msg.get("role") == "function" and msg.get("name") == FUNCTION_CALENDAR_FETCH_EVENTS:
                try:
                    calendar_data = json.loads(msg.get("content", "{}"))
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse calendar data from function response: {str(e)}")
                except Exception as e:
                    logger.error(f"Unexpected error parsing calendar data: {str(e)}", exc_info=True)
        
        return jsonify({
            'response': ai_response,
            'timestamp': response.created,
            'email_data': email_data,
            'calendar_data': calendar_data
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return jsonify({'error': 'An error occurred while processing your request'}), 500

@app.route('/api/health')
def health():
    """Health check endpoint for container orchestration"""
    return jsonify({'status': 'healthy', 'service': 'chat-bot'})

@app.route('/api/gmail/status')
def gmail_status():
    """Get Gmail integration status"""
    try:
        gmail_integration_instance, _, _, _, _, _ = get_user_integrations()
        status = gmail_integration_instance.check_status()
        logger.debug(f"Gmail status check - user_id: {gmail_integration_instance.user_id}, status: {status}")
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error checking Gmail status for user {gmail_integration_instance.user_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"Error checking Gmail status: {str(e)}"})

@app.route('/api/gmail/enable', methods=['POST'])
def gmail_enable():
    """Enable Gmail integration"""
    try:
        gmail_integration_instance, _, _, _, _, _ = get_user_integrations()
        logger.debug(f"Gmail enable - user_id: {gmail_integration_instance.user_id}")
        result = gmail_integration_instance.enable()
        logger.debug(f"Gmail enable result for user_id {gmail_integration_instance.user_id}: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error enabling Gmail for user {gmail_integration_instance.user_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"Error enabling Gmail: {str(e)}"})

@app.route('/api/calendar/status')
def calendar_status():
    """Get Google Calendar integration status"""
    try:
        _, calendar_integration_instance, _, _, _, _ = get_user_integrations()
        status = calendar_integration_instance.check_status()
        logger.debug(f"Calendar status check - user_id: {calendar_integration_instance.user_id}, status: {status}")
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error checking Calendar status for user {calendar_integration_instance.user_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"Error checking Calendar status: {str(e)}"})

@app.route('/api/calendar/enable', methods=['POST'])
def calendar_enable():
    """Enable Google Calendar integration"""
    try:
        _, calendar_integration_instance, _, _, _, _ = get_user_integrations()
        logger.debug(f"Calendar enable - user_id: {calendar_integration_instance.user_id}")
        result = calendar_integration_instance.enable()
        logger.debug(f"Calendar enable result for user_id {calendar_integration_instance.user_id}: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error enabling Calendar for user {calendar_integration_instance.user_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"Error enabling Calendar: {str(e)}"})

@app.route('/api/notion/status')
def notion_status():
    """Get Notion integration status"""
    try:
        _, _, notion_integration_instance, _, _, _ = get_user_integrations()
        status = notion_integration_instance.check_status()
        logger.debug(f"Notion status check - user_id: {notion_integration_instance.user_id}, status: {status}")
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error checking Notion status for user {notion_integration_instance.user_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"Error checking Notion status: {str(e)}"})

@app.route('/api/notion/enable', methods=['POST'])
def notion_enable():
    """Enable Notion integration"""
    try:
        _, _, notion_integration_instance, _, _, _ = get_user_integrations()
        logger.debug(f"Notion enable - user_id: {notion_integration_instance.user_id}")
        result = notion_integration_instance.enable()
        logger.debug(f"Notion enable result for user_id {notion_integration_instance.user_id}: {result}")
        
        # If result already has success field, return it as-is
        if isinstance(result, dict) and 'success' in result:
            return jsonify(result)
        else:
            return jsonify(result)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error enabling Notion for user {notion_integration_instance.user_id}: {error_msg}", exc_info=True)
        return jsonify({
            "success": False, 
            "message": f"Error enabling Notion: {error_msg}",
            "status": "error"
        })

@app.route('/api/github/status')
def github_status():
    """Get GitHub integration status"""
    try:
        _, _, _, github_integration_instance, _, _ = get_user_integrations()
        status = github_integration_instance.check_status()
        logger.debug(f"GitHub status check - user_id: {github_integration_instance.user_id}, status: {status}")
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error checking GitHub status for user {github_integration_instance.user_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"Error checking GitHub status: {str(e)}"})

@app.route('/api/github/enable', methods=['POST'])
def github_enable():
    """Enable GitHub integration"""
    try:
        _, _, _, github_integration_instance, _, _ = get_user_integrations()
        logger.debug(f"GitHub enable - user_id: {github_integration_instance.user_id}")
        result = github_integration_instance.enable()
        logger.debug(f"GitHub enable result for user_id {github_integration_instance.user_id}: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error enabling GitHub for user {github_integration_instance.user_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"Error enabling GitHub: {str(e)}"})

@app.route('/api/slack/status')
def slack_status():
    """Get Slack integration status"""
    try:
        _, _, _, _, slack_integration_instance, _ = get_user_integrations()
        status = slack_integration_instance.check_status()
        logger.debug(f"Slack status check - user_id: {slack_integration_instance.user_id}, status: {status}")
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error checking Slack status for user {slack_integration_instance.user_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"Error checking Slack status: {str(e)}"})

@app.route('/api/slack/enable', methods=['POST'])
def slack_enable():
    """Enable Slack integration"""
    try:
        _, _, _, _, slack_integration_instance, _ = get_user_integrations()
        logger.debug(f"Slack enable - user_id: {slack_integration_instance.user_id}")
        result = slack_integration_instance.enable()
        logger.debug(f"Slack enable result for user_id {slack_integration_instance.user_id}: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error enabling Slack for user {slack_integration_instance.user_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"Error enabling Slack: {str(e)}"})

@app.route('/api/hubspot/status')
def hubspot_status():
    """Get HubSpot integration status"""
    try:
        _, _, _, _, _, hubspot_integration_instance = get_user_integrations()
        status = hubspot_integration_instance.check_status()
        logger.debug(f"HubSpot status check - user_id: {hubspot_integration_instance.user_id}, status: {status}")
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error checking HubSpot status for user {hubspot_integration_instance.user_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"Error checking HubSpot status: {str(e)}"})

@app.route('/api/hubspot/enable', methods=['POST'])
def hubspot_enable():
    """Enable HubSpot integration"""
    try:
        _, _, _, _, _, hubspot_integration_instance = get_user_integrations()
        logger.debug(f"HubSpot enable - user_id: {hubspot_integration_instance.user_id}")
        result = hubspot_integration_instance.enable()
        logger.debug(f"HubSpot enable result for user_id {hubspot_integration_instance.user_id}: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error enabling HubSpot for user {hubspot_integration_instance.user_id}: {str(e)}", exc_info=True)
        return jsonify({"success": False, "message": f"Error enabling HubSpot: {str(e)}"})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
