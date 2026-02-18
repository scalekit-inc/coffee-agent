class ChatBot {
    constructor() {
        this.chatMessages = document.getElementById('chatMessages');
        this.chatForm = document.getElementById('chatForm');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        
        this.isLoading = false;
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.adjustTextareaHeight();
        this.initGmailToggle();
        this.initCalendarToggle();
        // this.initNotionToggle(); // Disabled - Notion integration hidden from UI
        this.initGitHubToggle();
        this.initSlackToggle();
        this.initHubSpotToggle();
    }
    
    setupEventListeners() {
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.messageInput.addEventListener('input', () => this.handleInput());
        this.messageInput.addEventListener('keydown', (e) => this.handleKeydown(e));
        
        // Gmail toggle event listener
        const gmailToggle = document.getElementById('gmailToggle');
        if (gmailToggle) {
            gmailToggle.addEventListener('change', (e) => this.handleGmailToggle(e));
        }
        
        // Calendar toggle event listener
        const calendarToggle = document.getElementById('calendarToggle');
        if (calendarToggle) {
            calendarToggle.addEventListener('change', (e) => this.handleCalendarToggle(e));
        }
        
        // Notion toggle event listener - Disabled (UI hidden)
        /*
        const notionToggle = document.getElementById('notionToggle');
        if (notionToggle) {
            notionToggle.addEventListener('change', (e) => this.handleNotionToggle(e));
        }
        */
        
        // GitHub toggle event listener
        const githubToggle = document.getElementById('githubToggle');
        if (githubToggle) {
            githubToggle.addEventListener('change', (e) => this.handleGitHubToggle(e));
        }
        
        // Slack toggle event listener
        const slackToggle = document.getElementById('slackToggle');
        if (slackToggle) {
            slackToggle.addEventListener('change', (e) => this.handleSlackToggle(e));
        }
        
        // HubSpot toggle event listener
        const hubspotToggle = document.getElementById('hubspotToggle');
        if (hubspotToggle) {
            hubspotToggle.addEventListener('change', (e) => this.handleHubSpotToggle(e));
        }
        
        // Modal event listeners
        const modalClose = document.getElementById('modalClose');
        const authCancel = document.getElementById('authCancel');
        const authDone = document.getElementById('authDone');
        
        if (modalClose) {
            modalClose.addEventListener('click', () => this.hideModal());
        }
        if (authCancel) {
            authCancel.addEventListener('click', () => this.hideModal());
        }
        if (authDone) {
            authDone.addEventListener('click', () => this.handleAuthDone());
        }
        
        // Calendar modal event listeners
        const calendarModalClose = document.getElementById('calendarModalClose');
        const calendarAuthCancel = document.getElementById('calendarAuthCancel');
        const calendarAuthDone = document.getElementById('calendarAuthDone');
        
        if (calendarModalClose) {
            calendarModalClose.addEventListener('click', () => this.hideCalendarModal());
        }
        if (calendarAuthCancel) {
            calendarAuthCancel.addEventListener('click', () => this.hideCalendarModal());
        }
        if (calendarAuthDone) {
            calendarAuthDone.addEventListener('click', () => this.handleCalendarAuthDone());
        }
        
        // Notion modal event listeners - Disabled (UI hidden)
        /*
        const notionModalClose = document.getElementById('notionModalClose');
        const notionAuthCancel = document.getElementById('notionAuthCancel');
        const notionAuthDone = document.getElementById('notionAuthDone');
        
        if (notionModalClose) {
            notionModalClose.addEventListener('click', () => this.hideNotionModal());
        }
        if (notionAuthCancel) {
            notionAuthCancel.addEventListener('click', () => this.hideNotionModal());
        }
        if (notionAuthDone) {
            notionAuthDone.addEventListener('click', () => this.handleNotionAuthDone());
        }
        */
        
        // Close modal when clicking outside
        const modal = document.getElementById('gmailModal');
        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideModal();
                }
            });
        }
        
        const calendarModal = document.getElementById('calendarModal');
        if (calendarModal) {
            calendarModal.addEventListener('click', (e) => {
                if (e.target === calendarModal) {
                    this.hideCalendarModal();
                }
            });
        }
        
        // Notion modal event listeners - Disabled (UI hidden)
        /*
        const notionModal = document.getElementById('notionModal');
        if (notionModal) {
            notionModal.addEventListener('click', (e) => {
                if (e.target === notionModal) {
                    this.hideNotionModal();
                }
            });
        }
        */
        
        // GitHub modal event listeners
        const githubModalClose = document.getElementById('githubModalClose');
        const githubAuthCancel = document.getElementById('githubAuthCancel');
        const githubAuthDone = document.getElementById('githubAuthDone');
        
        if (githubModalClose) {
            githubModalClose.addEventListener('click', () => this.hideGitHubModal());
        }
        if (githubAuthCancel) {
            githubAuthCancel.addEventListener('click', () => this.hideGitHubModal());
        }
        if (githubAuthDone) {
            githubAuthDone.addEventListener('click', () => this.handleGitHubAuthDone());
        }
        
        const githubModal = document.getElementById('githubModal');
        if (githubModal) {
            githubModal.addEventListener('click', (e) => {
                if (e.target === githubModal) {
                    this.hideGitHubModal();
                }
            });
        }
        
        // Slack modal event listeners
        const slackModalClose = document.getElementById('slackModalClose');
        const slackAuthCancel = document.getElementById('slackAuthCancel');
        const slackAuthDone = document.getElementById('slackAuthDone');
        
        if (slackModalClose) {
            slackModalClose.addEventListener('click', () => this.hideSlackModal());
        }
        if (slackAuthCancel) {
            slackAuthCancel.addEventListener('click', () => this.hideSlackModal());
        }
        if (slackAuthDone) {
            slackAuthDone.addEventListener('click', () => this.handleSlackAuthDone());
        }
        
        const slackModal = document.getElementById('slackModal');
        if (slackModal) {
            slackModal.addEventListener('click', (e) => {
                if (e.target === slackModal) {
                    this.hideSlackModal();
                }
            });
        }
        
        // HubSpot modal event listeners
        const hubspotModalClose = document.getElementById('hubspotModalClose');
        const hubspotAuthCancel = document.getElementById('hubspotAuthCancel');
        const hubspotAuthDone = document.getElementById('hubspotAuthDone');
        
        if (hubspotModalClose) {
            hubspotModalClose.addEventListener('click', () => this.hideHubSpotModal());
        }
        if (hubspotAuthCancel) {
            hubspotAuthCancel.addEventListener('click', () => this.hideHubSpotModal());
        }
        if (hubspotAuthDone) {
            hubspotAuthDone.addEventListener('click', () => this.handleHubSpotAuthDone());
        }
        
        const hubspotModal = document.getElementById('hubspotModal');
        if (hubspotModal) {
            hubspotModal.addEventListener('click', (e) => {
                if (e.target === hubspotModal) {
                    this.hideHubSpotModal();
                }
            });
        }
    }
    
    handleSubmit(e) {
        e.preventDefault();
        const message = this.messageInput.value.trim();
        
        if (!message || this.isLoading) return;
        
        this.sendMessage(message);
    }
    
    handleInput() {
        const message = this.messageInput.value.trim();
        this.sendButton.disabled = !message || this.isLoading;
        this.adjustTextareaHeight();
    }
    
    handleKeydown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.chatForm.dispatchEvent(new Event('submit'));
        }
    }
    
    adjustTextareaHeight() {
        this.messageInput.style.height = 'auto';
        this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
    }
    
    // Helper function to get headers with user info
    getUserHeaders() {
        return {
            'Content-Type': 'application/json'
        };
    }
    
    async sendMessage(message) {
        this.isLoading = true;
        this.sendButton.disabled = true;
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.messageInput.value = '';
        this.adjustTextareaHeight();
        
        // Show typing indicator
        const typingIndicator = this.showTypingIndicator();
        
        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: this.getUserHeaders(),
                body: JSON.stringify({ message })
            });
            
            const data = await response.json();
            
            // Remove typing indicator
            this.removeTypingIndicator(typingIndicator);
            
            // Check if there's an error in the response
            if (!response.ok || data.error) {
                const errorMessage = data.error || `HTTP error! status: ${response.status}`;
                console.error('Error from API:', errorMessage);
                this.addMessage(`❌ **Error**: ${errorMessage}`, 'ai');
                return;
            }
            
            // Add AI response
            if (data.response) {
                this.addMessage(data.response, 'ai');
            }
            
            // Display email data if available
            if (data.email_data && data.email_data.success) {
                this.displayEmails(data.email_data);
            }
                        
            // Display calendar data if available
            if (data.calendar_data && data.calendar_data.success) {
                if (data.calendar_data.event) {
                    // This is a created event
                    this.displayCreatedEvent(data.calendar_data);
                } else if (data.calendar_data.events) {
                    // This is fetched events
                    this.displayCalendarEvents(data.calendar_data);
                }
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.removeTypingIndicator(typingIndicator);
            this.addMessage(`❌ **Error**: ${error.message || 'Sorry, I encountered an error. Please try again.'}`, 'ai');
        } finally {
            this.isLoading = false;
            this.sendButton.disabled = false;
        }
    }
    
    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = sender === 'user' ? 'U' : '☕';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Handle markdown-like formatting for AI responses
        if (sender === 'ai') {
            messageContent.innerHTML = this.formatMessage(content);
        } else {
            const paragraph = document.createElement('p');
            paragraph.textContent = content;
            messageContent.appendChild(paragraph);
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // Simple markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }
    
    showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai-message typing-indicator-message';
        typingDiv.id = 'typingIndicator';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = '☕';
        
        const typingContent = document.createElement('div');
        typingContent.className = 'typing-indicator';
        typingContent.innerHTML = `
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        `;
        
        typingDiv.appendChild(avatar);
        typingDiv.appendChild(typingContent);
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
        
        return typingDiv;
    }
    
    removeTypingIndicator(typingIndicator) {
        if (typingIndicator && typingIndicator.parentNode) {
            typingIndicator.parentNode.removeChild(typingIndicator);
        }
    }
    
    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }
    
    displayEmails(emailData) {
        
        const emailDiv = document.createElement('div');
        emailDiv.className = 'message ai-message email-display';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = '📧';
        
        const emailContent = document.createElement('div');
        emailContent.className = 'message-content email-content';
        
        // Handle different email data formats
        let emails = [];
        if (emailData.emails && Array.isArray(emailData.emails)) {
            // Direct array of processed emails
            emails = emailData.emails;
        } else if (emailData.emails && emailData.emails.data && emailData.emails.data.messages) {
            // ScaleKit format: data.messages
            emails = emailData.emails.data.messages;
        } else if (emailData.data && emailData.data.messages) {
            // Alternative ScaleKit format
            emails = emailData.data.messages;
        } else {
            emailContent.innerHTML = '<p>No emails found.</p>';
            emailDiv.appendChild(avatar);
            emailDiv.appendChild(emailContent);
            this.chatMessages.appendChild(emailDiv);
            this.scrollToBottom();
            return;
        }
        
        if (emails.length === 0) {
            emailContent.innerHTML = '<p>No emails found.</p>';
        } else {
            const emailList = document.createElement('div');
            emailList.className = 'email-list';
            
            emails.forEach((email, index) => {
                const emailItem = document.createElement('div');
                emailItem.className = 'email-item';
                
                // Use processed email data if available, otherwise fall back to parsing headers
                let subject = email.subject || 'No Subject';
                let sender = email.sender || 'Unknown Sender';
                let date = email.date || 'Unknown Date';
                let snippet = email.snippet || 'No preview available';
                
                // Fallback: Extract information from payload.headers if processed data not available
                if (subject === 'No Subject' && email.payload && email.payload.headers) {
                    email.payload.headers.forEach(header => {
                        if (header.name === 'Subject') subject = header.value;
                        else if (header.name === 'From') sender = header.value;
                        else if (header.name === 'Date') date = header.value;
                    });
                }
                
                emailItem.innerHTML = `
                    <div class="email-header">
                        <strong class="email-subject">${subject}</strong>
                        <span class="email-sender">From: ${sender}</span>
                        <span class="email-date">${date}</span>
                    </div>
                    <div class="email-preview">${snippet}</div>
                `;
                
                emailList.appendChild(emailItem);
            });
            
            emailContent.appendChild(emailList);
        }
        
        emailDiv.appendChild(avatar);
        emailDiv.appendChild(emailContent);
        this.chatMessages.appendChild(emailDiv);
        this.scrollToBottom();
    }
    
    async initGmailToggle() {
        try {
            const response = await fetch('/api/gmail/status', {
                headers: this.getUserHeaders()
            });
            const data = await response.json();
            
            const gmailToggle = document.getElementById('gmailToggle');
            const gmailStatus = document.getElementById('gmailStatus');
            
            if (gmailToggle && gmailStatus) {
                gmailToggle.checked = data.enabled;
                gmailStatus.textContent = data.status === 'connected' ? 'Connected' : 'Disconnected';
                gmailStatus.className = `integration-status-badge ${data.enabled ? 'connected' : 'disconnected'}`;
            }
        } catch (error) {
            console.error('Failed to get Gmail status:', error);
        }
    }
    
    async handleGmailToggle(event) {
        const isEnabled = event.target.checked;
        const gmailStatus = document.getElementById('gmailStatus');
        
        try {
            if (isEnabled) {
                // Enable Gmail
                gmailStatus.textContent = 'Enabling...';
                const response = await fetch('/api/gmail/enable', { 
                    method: 'POST',
                    headers: this.getUserHeaders()
                });
                const data = await response.json();
                
                if (data.success) {
                                    if (data.status === 'needs_auth') {
                    // Show authorization modal
                    gmailStatus.textContent = 'Auth Required';
                    this.showAuthModal(data.auth_link);
                } else {
                    gmailStatus.textContent = 'Connected';
                    gmailStatus.className = 'integration-status-badge connected';
                        this.addMessage('✅ **Gmail Integration Enabled!**\n\nYour Gmail account is now connected. I can help you manage your emails efficiently.', 'ai');
                }
                } else {
                    event.target.checked = false;
                    gmailStatus.textContent = 'Error';
                    this.addMessage(`❌ **Gmail Integration Failed**\n\n${data.message}`, 'ai');
                }
            } else {
                // Disable Gmail
                    gmailStatus.textContent = 'Disconnected';
                    gmailStatus.className = 'integration-status-badge disconnected';
                    this.addMessage('🔴 **Gmail Integration Disabled**\n\nGmail features are now turned off.', 'ai');
            }
        } catch (error) {
            console.error('Gmail toggle error:', error);
            event.target.checked = !isEnabled;
            gmailStatus.textContent = 'Error';
            this.addMessage('❌ **Gmail Operation Failed**\n\nAn error occurred while updating Gmail integration.', 'ai');
        }
    }
    
    async initCalendarToggle() {
        try {
            const response = await fetch('/api/calendar/status', {
                headers: this.getUserHeaders()
            });
            const data = await response.json();
            
            const calendarToggle = document.getElementById('calendarToggle');
            const calendarStatus = document.getElementById('calendarStatus');
            
            if (calendarToggle && calendarStatus) {
                calendarToggle.checked = data.enabled;
                calendarStatus.textContent = data.status === 'connected' ? 'Connected' : 'Disconnected';
                calendarStatus.className = `integration-status-badge ${data.enabled ? 'connected' : 'disconnected'}`;
            }
        } catch (error) {
            console.error('Failed to get Calendar status:', error);
        }
    }
    
    async handleCalendarToggle(event) {
        const isEnabled = event.target.checked;
        const calendarStatus = document.getElementById('calendarStatus');
        
        try {
            if (isEnabled) {
                // Enable Google Calendar
                calendarStatus.textContent = 'Enabling...';
                const response = await fetch('/api/calendar/enable', { 
                    method: 'POST',
                    headers: this.getUserHeaders()
                });
            const data = await response.json();
            
            if (data.success) {
                    if (data.status === 'needs_auth') {
                        // Show authorization modal
                        calendarStatus.textContent = 'Auth Required';
                        this.showCalendarAuthModal(data.auth_link);
                    } else {
                        calendarStatus.textContent = 'Connected';
                        calendarStatus.className = 'integration-status-badge connected';
                        this.addMessage('✅ **Google Calendar Integration Enabled!**\n\nYour Google Calendar is now connected. I can help you manage your schedule efficiently.', 'ai');
                    }
                } else {
                    event.target.checked = false;
                    calendarStatus.textContent = 'Error';
                    this.addMessage(`❌ **Google Calendar Integration Failed**\n\n${data.message}`, 'ai');
                }
            } else {
                // Disable Google Calendar
                                    calendarStatus.textContent = 'Disconnected';
                    calendarStatus.className = 'integration-status-badge disconnected';
                this.addMessage('🔴 **Google Calendar Integration Disabled**\n\nGoogle Calendar features are now turned off.', 'ai');
            }
        } catch (error) {
            console.error('Calendar toggle error:', error);
            event.target.checked = !isEnabled;
            calendarStatus.textContent = 'Error';
            this.addMessage('❌ **Google Calendar Operation Failed**\n\nAn error occurred while updating Google Calendar integration.', 'ai');
        }
    }
    
    showAuthModal(authLink) {
        const modal = document.getElementById('gmailModal');
        const authLinkElement = document.getElementById('authLink');
        
        if (modal && authLinkElement) {
            authLinkElement.href = authLink;
            modal.style.display = 'block';
        }
    }
    
    hideModal() {
        const modal = document.getElementById('gmailModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    async handleAuthDone() {
        const gmailToggle = document.getElementById('gmailToggle');
        const gmailStatus = document.getElementById('gmailStatus');
        
        try {
            gmailStatus.textContent = 'Checking...';
            this.hideModal();
            
            // Check the Gmail status again
            const response = await fetch('/api/gmail/status', {
                headers: this.getUserHeaders()
            });
            const data = await response.json();
            
            if (data.success && data.enabled) {
                gmailToggle.checked = true;
                gmailStatus.textContent = 'Connected';
                gmailStatus.className = 'integration-status-badge connected';
                                        this.addMessage('✅ **Gmail Authorization Complete!**\n\nYour Gmail account is now connected. I can help you manage your emails efficiently.', 'ai');
            } else {
                gmailToggle.checked = false;
                gmailStatus.textContent = 'Not Connected';
                gmailStatus.className = 'integration-status-badge disconnected';
                this.addMessage('❌ **Authorization Not Complete**\n\nPlease complete the Gmail authorization process and try again.', 'ai');
            }
        } catch (error) {
            console.error('Auth check error:', error);
            gmailStatus.textContent = 'Error';
            this.addMessage('❌ **Connection Check Failed**\n\nAn error occurred while checking the connection status.', 'ai');
        }
    }
    
    showCalendarAuthModal(authLink) {
        const modal = document.getElementById('calendarModal');
        const authLinkElement = document.getElementById('calendarAuthLink');
        
        if (modal && authLinkElement) {
            authLinkElement.href = authLink;
            modal.style.display = 'block';
        }
    }
    
    hideCalendarModal() {
        const modal = document.getElementById('calendarModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    async handleCalendarAuthDone() {
        const calendarToggle = document.getElementById('calendarToggle');
        const calendarStatus = document.getElementById('calendarStatus');
        
        try {
            calendarStatus.textContent = 'Checking...';
            this.hideCalendarModal();
            
            // Check the Calendar status again
            const response = await fetch('/api/calendar/status', {
                headers: this.getUserHeaders()
            });
            const data = await response.json();
            
            if (data.success && data.enabled) {
                calendarToggle.checked = true;
                calendarStatus.textContent = 'Connected';
                calendarStatus.className = 'integration-status-badge connected';
                                        this.addMessage('✅ **Google Calendar Authorization Complete!**\n\nYour Google Calendar account is now connected. I can help you manage your schedule efficiently.', 'ai');
            } else {
                calendarToggle.checked = false;
                calendarStatus.textContent = 'Not Connected';
                calendarStatus.className = 'integration-status-badge disconnected';
                this.addMessage('❌ **Authorization Not Complete**\n\nPlease complete the Google Calendar authorization process and try again.', 'ai');
            }
        } catch (error) {
            console.error('Calendar auth check error:', error);
            calendarStatus.textContent = 'Error';
            this.addMessage('❌ **Connection Check Failed**\n\nAn error occurred while checking the connection status.', 'ai');
        }
    }
    
    // Notion Integration Methods - Disabled (UI hidden)
    /*
    showNotionAuthModal(authLink) {
        const modal = document.getElementById('notionModal');
        const authLinkElement = document.getElementById('notionAuthLink');
        
        if (modal && authLinkElement) {
            authLinkElement.href = authLink;
            modal.style.display = 'block';
        }
    }
    
    hideNotionModal() {
        const modal = document.getElementById('notionModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    async handleNotionAuthDone() {
        const notionToggle = document.getElementById('notionToggle');
        const notionStatus = document.getElementById('notionStatus');
        
        try {
            notionStatus.textContent = 'Checking...';
            this.hideNotionModal();
            
            // Check the Notion status again
            const response = await fetch('/api/notion/status', {
                headers: this.getUserHeaders()
            });
            const data = await response.json();
            
            if (data.success && data.enabled) {
                notionToggle.checked = true;
                notionStatus.textContent = 'Connected';
                notionStatus.className = 'integration-status-badge connected';
                this.addMessage('✅ **Notion Authorization Complete!**\n\nYour Notion account is now connected. I can help you create and search Notion pages efficiently.', 'ai');
            } else {
                notionToggle.checked = false;
                notionStatus.textContent = 'Not Connected';
                notionStatus.className = 'integration-status-badge disconnected';
                this.addMessage('❌ **Authorization Not Complete**\n\nPlease complete the Notion authorization process and try again.', 'ai');
            }
        } catch (error) {
            console.error('Notion auth check error:', error);
            notionStatus.textContent = 'Error';
            this.addMessage('❌ **Connection Check Failed**\n\nAn error occurred while checking the connection status.', 'ai');
        }
    }
    
    async initNotionToggle() {
        try {
            const response = await fetch('/api/notion/status', {
                headers: this.getUserHeaders()
            });
            const data = await response.json();
            
            const notionToggle = document.getElementById('notionToggle');
            const notionStatus = document.getElementById('notionStatus');
            
            if (notionToggle && notionStatus) {
                notionToggle.checked = data.enabled;
                notionStatus.textContent = data.status === 'connected' ? 'Connected' : 'Disconnected';
                notionStatus.className = `integration-status-badge ${data.enabled ? 'connected' : 'disconnected'}`;
            }
        } catch (error) {
            console.error('Failed to get Notion status:', error);
        }
    }
    
    async handleNotionToggle(event) {
        const isEnabled = event.target.checked;
        const notionStatus = document.getElementById('notionStatus');
        
        try {
            if (isEnabled) {
                // Enable Notion
                notionStatus.textContent = 'Enabling...';
                const response = await fetch('/api/notion/enable', { 
                    method: 'POST',
                    headers: this.getUserHeaders()
                });
                const data = await response.json();
                
                if (data.success) {
                    if (data.status === 'needs_auth') {
                        // Show authorization modal
                        notionStatus.textContent = 'Auth Required';
                        this.showNotionAuthModal(data.auth_link);
                    } else {
                        notionStatus.textContent = 'Connected';
                        notionStatus.className = 'integration-status-badge connected';
                        this.addMessage('✅ **Notion Integration Enabled!**\n\nYour Notion account is now connected. I can help you create and search Notion pages.', 'ai');
                    }
                } else {
                    event.target.checked = false;
                    notionStatus.textContent = 'Error';
                    this.addMessage(`❌ **Notion Integration Failed**\n\n${data.message}`, 'ai');
                }
            } else {
                // Disable Notion
                notionStatus.textContent = 'Disconnected';
                notionStatus.className = 'integration-status-badge disconnected';
                this.addMessage('🔴 **Notion Integration Disabled**\n\nNotion features are now turned off.', 'ai');
            }
        } catch (error) {
            console.error('Notion toggle error:', error);
            event.target.checked = !isEnabled;
            notionStatus.textContent = 'Error';
            this.addMessage('❌ **Notion Operation Failed**\n\nAn error occurred while updating Notion integration.', 'ai');
        }
    }
    */
    
    displayCalendarEvents(calendarData) {
        // Handle different calendar data formats
        let events = [];
        if (calendarData.events && Array.isArray(calendarData.events)) {
            // Direct array of processed events
            events = calendarData.events;
        } else if (calendarData.events && calendarData.events.data && calendarData.events.data.events) {
            // ScaleKit format: data.events
            events = calendarData.events.data.events;
        } else if (calendarData.data && calendarData.data.events) {
            // Alternative ScaleKit format
            events = calendarData.data.events;
        } else {
            // No events found
            const calendarDiv = document.createElement('div');
            calendarDiv.className = 'message ai-message calendar-display';
            
            const avatar = document.createElement('div');
            avatar.className = 'message-avatar';
            avatar.textContent = '📅';
            
            const calendarContent = document.createElement('div');
            calendarContent.className = 'message-content calendar-content';
            calendarContent.innerHTML = '<p>No calendar events found.</p>';
            
            calendarDiv.appendChild(avatar);
            calendarDiv.appendChild(calendarContent);
            this.chatMessages.appendChild(calendarDiv);
            this.scrollToBottom();
            return;
        }
        
        const calendarDiv = document.createElement('div');
        calendarDiv.className = 'message ai-message calendar-display';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = '📅';
        
        const calendarContent = document.createElement('div');
        calendarContent.className = 'message-content calendar-content';
        
        // Events array is already defined above
        
        if (events.length === 0) {
            calendarContent.innerHTML = '<p>No calendar events found.</p>';
        } else {
            const calendarList = document.createElement('div');
            calendarList.className = 'calendar-list';
            
            events.forEach((event, index) => {
                const eventItem = document.createElement('div');
                eventItem.className = 'calendar-item';
                
                // Use processed event data if available
                const title = event.summary || 'No Title';
                const organizer = event.organizer?.email || 'Unknown Organizer';
                const startTime = event.start?.dateTime || event.start?.date || 'Unknown Time';
                const endTime = event.end?.dateTime || event.end?.date || 'Unknown Time';
                const description = event.description || 'No description available';
                const conferenceData = event.conferenceData || {};
                
                // Format time display nicely
                let timeDisplay = 'Unknown Time';
                if (startTime !== 'Unknown Time' && endTime !== 'Unknown Time') {
                    try {
                        const startDate = new Date(startTime);
                        const endDate = new Date(endTime);
                        
                        if (!isNaN(startDate.getTime()) && !isNaN(endDate.getTime())) {
                            const startFormatted = startDate.toLocaleString('en-US', {
                                weekday: 'short',
                                month: 'short',
                                day: 'numeric',
                                hour: 'numeric',
                                minute: '2-digit',
                                hour12: true,
                                timeZoneName: 'short'
                            });
                            
                            const endFormatted = endDate.toLocaleString('en-US', {
                                hour: 'numeric',
                                minute: '2-digit',
                                hour12: true,
                                timeZoneName: 'short'
                            });
                            
                            timeDisplay = `${startFormatted} - ${endFormatted}`;
                        } else {
                            timeDisplay = `${startTime} - ${endTime}`;
                        }
                    } catch (e) {
                        timeDisplay = `${startTime} - ${endTime}`;
                    }
                }
                
                // Extract name from email for better display
                let organizerDisplay = organizer;
                if (organizer.includes('@')) {
                    const namePart = organizer.split('@')[0];
                    organizerDisplay = namePart.split('.').map(word => 
                        word.charAt(0).toUpperCase() + word.slice(1)
                    ).join(' ');
                }
                
                eventItem.innerHTML = `
                    <div class="calendar-header">
                        <strong class="calendar-title">${title}</strong>
                        <span class="calendar-organizer">Organized by: ${organizerDisplay}</span>
                        <span class="calendar-time">${timeDisplay}</span>
                    </div>
                    <div class="calendar-description">${description}</div>
                `;
                
                // Add conference data if available
                if (conferenceData.entryPoints && conferenceData.entryPoints.length > 0) {
                    const conferenceDiv = document.createElement('div');
                    conferenceDiv.className = 'calendar-conference';
                    
                    const videoEntry = conferenceData.entryPoints.find(ep => ep.entryPointType === 'video');
                    if (videoEntry) {
                        conferenceDiv.innerHTML = `
                            <div class="calendar-conference-title">📹 Meeting Link</div>
                            <a href="${videoEntry.uri}" target="_blank" class="calendar-conference-link">${videoEntry.label || 'Join Meeting'}</a>
                        `;
                        eventItem.appendChild(conferenceDiv);
                    }
                }
                
                calendarList.appendChild(eventItem);
            });
            
            calendarContent.appendChild(calendarList);
        }
        
        calendarDiv.appendChild(avatar);
        calendarDiv.appendChild(calendarContent);
        this.chatMessages.appendChild(calendarDiv);
        this.scrollToBottom();
    }
    
    displayCreatedEvent(calendarData) {
        if (!calendarData.event) return;
        
        const calendarDiv = document.createElement('div');
        calendarDiv.className = 'message ai-message calendar-display';
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = '✅';
        
        const calendarContent = document.createElement('div');
        calendarContent.className = 'message-content calendar-content';
        
        const event = calendarData.event;
        const title = event.summary || 'No Title';
        const startTime = event.start?.dateTime || event.start?.date || 'Unknown Time';
        const endTime = event.end?.dateTime || event.end?.date || 'Unknown Time';
        const description = event.description || 'No description available';
        const location = event.location || '';
        const htmlLink = event.htmlLink || '';
        
        // Format time display nicely
        let timeDisplay = 'Unknown Time';
        if (startTime !== 'Unknown Time' && endTime !== 'Unknown Time') {
            try {
                const startDate = new Date(startTime);
                const endDate = new Date(endTime);
                
                if (!isNaN(startDate.getTime()) && !isNaN(endDate.getTime())) {
                    const startFormatted = startDate.toLocaleString('en-US', {
                        weekday: 'short',
                        month: 'short',
                        day: 'numeric',
                        hour: 'numeric',
                        minute: '2-digit',
                        hour12: true,
                        timeZoneName: 'short'
                    });
                    
                    const endFormatted = endDate.toLocaleString('en-US', {
                        hour: 'numeric',
                        minute: '2-digit',
                        hour12: true,
                        timeZoneName: 'short'
                    });
                    
                    timeDisplay = `${startFormatted} - ${endFormatted}`;
                } else {
                    timeDisplay = `${startTime} - ${endTime}`;
                }
            } catch (e) {
                timeDisplay = `${startTime} - ${endTime}`;
            }
        }
        
        calendarContent.innerHTML = `
            <div class="calendar-header">
                <strong class="calendar-title">✅ Event Created: ${title}</strong>
                <span class="calendar-time">${timeDisplay}</span>
            </div>
            ${description ? `<div class="calendar-description">${description}</div>` : ''}
            ${location ? `<div class="calendar-location">📍 ${location}</div>` : ''}
            ${htmlLink ? `<div class="calendar-link"><a href="${htmlLink}" target="_blank">📅 View in Google Calendar</a></div>` : ''}
        `;
        
        calendarDiv.appendChild(avatar);
        calendarDiv.appendChild(calendarContent);
        this.chatMessages.appendChild(calendarDiv);
        this.scrollToBottom();
    }
    
    async initGitHubToggle() {
        try {
            const response = await fetch('/api/github/status', {
                headers: this.getUserHeaders()
            });
            const data = await response.json();
            
            const githubToggle = document.getElementById('githubToggle');
            const githubStatus = document.getElementById('githubStatus');
            
            if (githubToggle && githubStatus) {
                githubToggle.checked = data.enabled;
                githubStatus.textContent = data.status === 'connected' ? 'Connected' : 'Disconnected';
                githubStatus.className = `integration-status-badge ${data.enabled ? 'connected' : 'disconnected'}`;
            }
        } catch (error) {
            console.error('Failed to get GitHub status:', error);
        }
    }
    
    async handleGitHubToggle(event) {
        const isEnabled = event.target.checked;
        const githubStatus = document.getElementById('githubStatus');
        
        try {
            if (isEnabled) {
                // Enable GitHub
                githubStatus.textContent = 'Enabling...';
                const response = await fetch('/api/github/enable', { 
                    method: 'POST',
                    headers: this.getUserHeaders()
                });
                const data = await response.json();
                
                if (data.success) {
                    if (data.status === 'needs_auth') {
                        // Show authorization modal
                        githubStatus.textContent = 'Auth Required';
                        this.showGitHubAuthModal(data.auth_link);
                    } else {
                        githubStatus.textContent = 'Connected';
                        githubStatus.className = 'integration-status-badge connected';
                        this.addMessage('✅ **GitHub Integration Enabled!**\n\nYour GitHub account is now connected. I can help you manage your repositories and issues.', 'ai');
                    }
                } else {
                    event.target.checked = false;
                    githubStatus.textContent = 'Error';
                    this.addMessage(`❌ **GitHub Integration Failed**\n\n${data.message}`, 'ai');
                }
            } else {
                // Disable GitHub
                githubStatus.textContent = 'Disconnected';
                githubStatus.className = 'integration-status-badge disconnected';
                this.addMessage('🔴 **GitHub Integration Disabled**\n\nGitHub features are now turned off.', 'ai');
            }
        } catch (error) {
            console.error('GitHub toggle error:', error);
            event.target.checked = !isEnabled;
            githubStatus.textContent = 'Error';
            this.addMessage('❌ **GitHub Operation Failed**\n\nAn error occurred while updating GitHub integration.', 'ai');
        }
    }
    
    showGitHubAuthModal(authLink) {
        const modal = document.getElementById('githubModal');
        const authLinkElement = document.getElementById('githubAuthLink');
        
        if (modal && authLinkElement) {
            authLinkElement.href = authLink;
            modal.style.display = 'block';
        }
    }
    
    hideGitHubModal() {
        const modal = document.getElementById('githubModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    async handleGitHubAuthDone() {
        const githubToggle = document.getElementById('githubToggle');
        const githubStatus = document.getElementById('githubStatus');
        
        try {
            githubStatus.textContent = 'Checking...';
            this.hideGitHubModal();
            
            // Check the GitHub status again
            const response = await fetch('/api/github/status', {
                headers: this.getUserHeaders()
            });
            const data = await response.json();
            
            if (data.success && data.enabled) {
                githubToggle.checked = true;
                githubStatus.textContent = 'Connected';
                githubStatus.className = 'integration-status-badge connected';
                this.addMessage('✅ **GitHub Authorization Complete!**\n\nYour GitHub account is now connected. I can help you manage your repositories and issues efficiently.', 'ai');
            } else {
                githubToggle.checked = false;
                githubStatus.textContent = 'Not Connected';
                githubStatus.className = 'integration-status-badge disconnected';
                this.addMessage('❌ **Authorization Not Complete**\n\nPlease complete the GitHub authorization process and try again.', 'ai');
            }
        } catch (error) {
            console.error('GitHub auth check error:', error);
            githubStatus.textContent = 'Error';
            this.addMessage('❌ **Connection Check Failed**\n\nAn error occurred while checking the connection status.', 'ai');
        }
    }
    
    async initSlackToggle() {
        try {
            const response = await fetch('/api/slack/status', {
                headers: this.getUserHeaders()
            });
            const data = await response.json();
            
            const slackToggle = document.getElementById('slackToggle');
            const slackStatus = document.getElementById('slackStatus');
            
            if (slackToggle && slackStatus) {
                slackToggle.checked = data.enabled;
                slackStatus.textContent = data.status === 'connected' ? 'Connected' : 'Disconnected';
                slackStatus.className = `integration-status-badge ${data.enabled ? 'connected' : 'disconnected'}`;
            }
        } catch (error) {
            console.error('Failed to get Slack status:', error);
        }
    }
    
    async handleSlackToggle(event) {
        const isEnabled = event.target.checked;
        const slackStatus = document.getElementById('slackStatus');
        
        try {
            if (isEnabled) {
                // Enable Slack
                slackStatus.textContent = 'Enabling...';
                const response = await fetch('/api/slack/enable', { 
                    method: 'POST',
                    headers: this.getUserHeaders()
                });
                const data = await response.json();
                
                if (data.success) {
                    if (data.status === 'needs_auth') {
                        // Show authorization modal
                        slackStatus.textContent = 'Auth Required';
                        this.showSlackAuthModal(data.auth_link);
                    } else {
                        slackStatus.textContent = 'Connected';
                        slackStatus.className = 'integration-status-badge connected';
                        this.addMessage('✅ **Slack Integration Enabled!**\n\nYour Slack workspace is now connected. I can help you manage your channels and messages.', 'ai');
                    }
                } else {
                    event.target.checked = false;
                    slackStatus.textContent = 'Error';
                    this.addMessage(`❌ **Slack Integration Failed**\n\n${data.message}`, 'ai');
                }
            } else {
                // Disable Slack
                slackStatus.textContent = 'Disconnected';
                slackStatus.className = 'integration-status-badge disconnected';
                this.addMessage('🔴 **Slack Integration Disabled**\n\nSlack features are now turned off.', 'ai');
            }
        } catch (error) {
            console.error('Slack toggle error:', error);
            event.target.checked = !isEnabled;
            slackStatus.textContent = 'Error';
            this.addMessage('❌ **Slack Operation Failed**\n\nAn error occurred while updating Slack integration.', 'ai');
        }
    }
    
    showSlackAuthModal(authLink) {
        const modal = document.getElementById('slackModal');
        const authLinkElement = document.getElementById('slackAuthLink');
        
        if (modal && authLinkElement) {
            authLinkElement.href = authLink;
            modal.style.display = 'block';
        }
    }
    
    hideSlackModal() {
        const modal = document.getElementById('slackModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    async handleSlackAuthDone() {
        const slackToggle = document.getElementById('slackToggle');
        const slackStatus = document.getElementById('slackStatus');
        
        try {
            slackStatus.textContent = 'Checking...';
            this.hideSlackModal();
            
            // Check the Slack status again
            const response = await fetch('/api/slack/status', {
                headers: this.getUserHeaders()
            });
            const data = await response.json();
            
            if (data.success && data.enabled) {
                slackToggle.checked = true;
                slackStatus.textContent = 'Connected';
                slackStatus.className = 'integration-status-badge connected';
                this.addMessage('✅ **Slack Authorization Complete!**\n\nYour Slack workspace is now connected. I can help you manage your channels and messages efficiently.', 'ai');
            } else {
                slackToggle.checked = false;
                slackStatus.textContent = 'Not Connected';
                slackStatus.className = 'integration-status-badge disconnected';
                this.addMessage('❌ **Authorization Not Complete**\n\nPlease complete the Slack authorization process and try again.', 'ai');
            }
        } catch (error) {
            console.error('Slack auth check error:', error);
            slackStatus.textContent = 'Error';
            this.addMessage('❌ **Connection Check Failed**\n\nAn error occurred while checking the connection status.', 'ai');
        }
    }
    
    async initHubSpotToggle() {
        try {
            const response = await fetch('/api/hubspot/status', {
                headers: this.getUserHeaders()
            });
            const data = await response.json();
            
            const hubspotToggle = document.getElementById('hubspotToggle');
            const hubspotStatus = document.getElementById('hubspotStatus');
            
            if (hubspotToggle && hubspotStatus) {
                hubspotToggle.checked = data.enabled;
                hubspotStatus.textContent = data.status === 'connected' ? 'Connected' : 'Disconnected';
                hubspotStatus.className = `integration-status-badge ${data.enabled ? 'connected' : 'disconnected'}`;
            }
        } catch (error) {
            console.error('Failed to get HubSpot status:', error);
        }
    }
    
    async handleHubSpotToggle(event) {
        const isEnabled = event.target.checked;
        const hubspotStatus = document.getElementById('hubspotStatus');
        
        try {
            if (isEnabled) {
                // Enable HubSpot
                hubspotStatus.textContent = 'Enabling...';
                const response = await fetch('/api/hubspot/enable', { 
                    method: 'POST',
                    headers: this.getUserHeaders()
                });
                const data = await response.json();
                
                if (data.success) {
                    if (data.status === 'needs_auth') {
                        // Show authorization modal
                        hubspotStatus.textContent = 'Auth Required';
                        this.showHubSpotAuthModal(data.auth_link);
                    } else {
                        hubspotStatus.textContent = 'Connected';
                        hubspotStatus.className = 'integration-status-badge connected';
                        this.addMessage('✅ **HubSpot Integration Enabled!**\n\nYour HubSpot CRM is now connected. I can help you manage your contacts and companies.', 'ai');
                    }
                } else {
                    event.target.checked = false;
                    hubspotStatus.textContent = 'Error';
                    this.addMessage(`❌ **HubSpot Integration Failed**\n\n${data.message}`, 'ai');
                }
            } else {
                // Disable HubSpot
                hubspotStatus.textContent = 'Disconnected';
                hubspotStatus.className = 'integration-status-badge disconnected';
                this.addMessage('🔴 **HubSpot Integration Disabled**\n\nHubSpot features are now turned off.', 'ai');
            }
        } catch (error) {
            console.error('HubSpot toggle error:', error);
            event.target.checked = !isEnabled;
            hubspotStatus.textContent = 'Error';
            this.addMessage('❌ **HubSpot Operation Failed**\n\nAn error occurred while updating HubSpot integration.', 'ai');
        }
    }
    
    showHubSpotAuthModal(authLink) {
        const modal = document.getElementById('hubspotModal');
        const authLinkElement = document.getElementById('hubspotAuthLink');
        
        if (modal && authLinkElement) {
            authLinkElement.href = authLink;
            modal.style.display = 'block';
        }
    }
    
    hideHubSpotModal() {
        const modal = document.getElementById('hubspotModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    async handleHubSpotAuthDone() {
        const hubspotToggle = document.getElementById('hubspotToggle');
        const hubspotStatus = document.getElementById('hubspotStatus');
        
        try {
            hubspotStatus.textContent = 'Checking...';
            this.hideHubSpotModal();
            
            // Check the HubSpot status again
            const response = await fetch('/api/hubspot/status', {
                headers: this.getUserHeaders()
            });
            const data = await response.json();
            
            if (data.success && data.enabled) {
                hubspotToggle.checked = true;
                hubspotStatus.textContent = 'Connected';
                hubspotStatus.className = 'integration-status-badge connected';
                this.addMessage('✅ **HubSpot Authorization Complete!**\n\nYour HubSpot CRM is now connected. I can help you manage your contacts and companies efficiently.', 'ai');
            } else {
                hubspotToggle.checked = false;
                hubspotStatus.textContent = 'Not Connected';
                hubspotStatus.className = 'integration-status-badge disconnected';
                this.addMessage('❌ **Authorization Not Complete**\n\nPlease complete the HubSpot authorization process and try again.', 'ai');
            }
        } catch (error) {
            console.error('HubSpot auth check error:', error);
            hubspotStatus.textContent = 'Error';
            this.addMessage('❌ **Connection Check Failed**\n\nAn error occurred while checking the connection status.', 'ai');
        }
    }
}

// Initialize the chat bot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChatBot();
});
