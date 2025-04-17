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
    
    let chatHistory = [];
    
    // Toggle chat popup
    aiChatButton.addEventListener('click', function() {
        aiChatPopup.style.display = 'flex';
        aiChatButton.style.display = 'none';
    });
    
    // Minimize chat
    minimizeChat.addEventListener('click', function() {
        aiChatPopup.style.display = 'none';
        aiChatButton.style.display = 'flex';
    });
    
    // Close chat
    closeChat.addEventListener('click', function() {
        aiChatPopup.style.display = 'none';
        aiChatButton.style.display = 'flex';
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
        
        // Xử lý định dạng tin nhắn 
        if (sender === 'ai') {
            // Xử lý định dạng tin nhắn
            let formattedMessage = message
                // Tách thành các dòng để xử lý danh sách
                .split('\n');
                
            // Xử lý từng dòng
            formattedMessage = formattedMessage.map(line => {
                // Xử lý danh sách số
                if (/^\d+\.\s/.test(line)) {
                    return `<p class="list-numbered">${line.replace(/(\d+\.\s+)(\*\*[^*]+\*\*:?)/, '<span class="list-number">$1</span><strong>$2</strong>')}</p>`;
                }
                // Xử lý danh sách gạch đầu dòng
                else if (/^[\-\*]\s/.test(line)) {
                    return `<p class="list-bullet">${line.replace(/^[\-\*]\s+/, '<span class="bullet-point">•</span> ')}</p>`;
                }
                // Dòng thường
                else if (line.trim()) {
                    return `<p>${line}</p>`;
                }
                // Dòng trống
                return '';
            }).join('');
            
            // Xử lý in đậm và in nghiêng
            formattedMessage = formattedMessage
                .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
                .replace(/\*([^*]+)\*/g, '<em>$1</em>');
            
            messageContent.innerHTML = formattedMessage;
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
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message ai-message typing-indicator-container';
        typingDiv.id = 'typingIndicator';
        
        const typingContent = document.createElement('div');
        typingContent.className = 'message-content';
        
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'typing-indicator';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.className = 'typing-dot';
            typingIndicator.appendChild(dot);
        }
        
        typingContent.appendChild(typingIndicator);
        typingDiv.appendChild(typingContent);
        
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
        // Show typing indicator
        showTypingIndicator();
        
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