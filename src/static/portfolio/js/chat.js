/**
 * AI Chat functionality for Portfolio Management System
 */
document.addEventListener('DOMContentLoaded', function() {
    const aiChatButton = document.getElementById('aiChatButton');
    const aiChatPopup = document.getElementById('aiChatPopup');
    const minimizeChat = document.getElementById('minimizeChat');
    const closeChat = document.getElementById('closeChat');
    const chatForm = document.getElementById('chatForm');
    const userMessage = document.getElementById('userMessage');
    const chatMessages = document.getElementById('chatMessages');
    const suggestedItems = document.querySelectorAll('.suggested-item');
    
    let chatHistory = [];
    
    // Toggle chat popup
    aiChatButton.addEventListener('click', function() {
        aiChatPopup.style.display = 'flex';
        
        // Add animation after display is set
        setTimeout(() => {
            aiChatPopup.classList.add('show-animation');
        }, 10);
        
        aiChatButton.style.display = 'none';
        
        // Scroll to the bottom of the chat messages
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // Focus the input field
        setTimeout(() => {
            userMessage.focus();
        }, 300);
    });
    
    // Minimize chat
    minimizeChat.addEventListener('click', function() {
        // First remove the animation class
        aiChatPopup.classList.remove('show-animation');
        
        // Then hide after animation completes
        setTimeout(() => {
            aiChatPopup.style.display = 'none';
            aiChatButton.style.display = 'flex';
        }, 300);
    });
    
    // Close chat
    closeChat.addEventListener('click', function() {
        // First remove the animation class
        aiChatPopup.classList.remove('show-animation');
        
        // Then hide after animation completes
        setTimeout(() => {
            aiChatPopup.style.display = 'none';
            aiChatButton.style.display = 'flex';
        }, 300);
    });
    
    // Handle suggested questions
    suggestedItems.forEach(item => {
        item.addEventListener('click', function() {
            const question = this.getAttribute('data-question');
            userMessage.value = question;
            
            // Hide the suggested questions section
            const suggestedQuestionsSection = document.getElementById('suggestedQuestions');
            if (suggestedQuestionsSection) {
                suggestedQuestionsSection.style.display = 'none';
            }
            
            // Submit the form
            const event = new Event('submit', {
                'bubbles': true,
                'cancelable': true
            });
            chatForm.dispatchEvent(event);
        });
    });
    
    // Handle sending messages
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = userMessage.value.trim();
        if (message) {
            // Add user message to chat
            addMessage(message, 'user');
            userMessage.value = '';
            
            // Show typing indicator
            showTypingIndicator();
            
            // Call API
            callGeminiAPI(message);
        }
    });
    
    function addMessage(message, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        // Create text node directly to avoid rendering issues with special characters
        if (sender === 'ai') {
            // Split message by newlines but retain clean text
            const paragraphs = message.split('\n').filter(line => line.trim() !== '');
            
            paragraphs.forEach(para => {
                const p = document.createElement('p');
                // Use textContent instead of innerHTML to avoid rendering issues
                p.textContent = para.replace(/\*\*/g, '').replace(/\*/g, '');
                messageContent.appendChild(p);
            });
        } else {
            const messageParagraph = document.createElement('p');
            messageParagraph.textContent = message;
            messageContent.appendChild(messageParagraph);
        }
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // Add to chat history
        chatHistory.push({
            role: sender === 'user' ? 'user' : 'assistant',
            content: message
        });
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function showTypingIndicator() {
        // Remove any existing typing indicators
        removeTypingIndicator();
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai-message';
        typingDiv.id = 'typingIndicator';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const typingText = document.createElement('p');
        typingText.textContent = 'Đang trả lời...';
        messageContent.appendChild(typingText);
        
        typingDiv.appendChild(messageContent);
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function removeTypingIndicator() {
        const typingIndicator = document.getElementById('typingIndicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    function callGeminiAPI(message) {
        // Call Django API endpoint
        fetch('/api/ai-chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Remove typing indicator
            removeTypingIndicator();
            
            if (data.success) {
                // Add AI response to chat
                addMessage(data.response, 'ai');
            } else {
                // Show error message
                addMessage('Xin lỗi, đã xảy ra lỗi: ' + data.error, 'ai');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            
            // Remove typing indicator
            removeTypingIndicator();
            
            // Show error message
            addMessage('Xin lỗi, đã xảy ra lỗi khi xử lý yêu cầu của bạn. Vui lòng thử lại sau.', 'ai');
        });
    }
}); 