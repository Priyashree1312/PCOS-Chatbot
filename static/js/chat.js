// static/js/chat.js - FINAL WORKING VERSION
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.getElementById('messages');
    const questionInput = document.getElementById('question');
    const sendBtn = document.getElementById('sendBtn');

    function sendMessage() {
        const question = questionInput.value.trim();
        if (!question) return;

        addMessage(question, 'user-message');
        questionInput.value = '';
        addMessage('Pinky is typing...', 'bot-message typing');

        // 🔥 FIXED URL - THIS WAS THE PROBLEM!
        fetch('/chat/chat/', {  
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({question: question})
        })
        .then(response => {
            if (!response.ok) throw new Error('Network error');
            return response.json();
        })
        .then(data => {
            removeTyping();
            console.log('✅ API Response:', data);
            addMessage(data.answer || 'No response', 'bot-message');
        })
        .catch(error => {
            console.error('❌ Error:', error);
            removeTyping();
            addMessage('🌩️ Oops! Try again 💕', 'bot-message');
        });
    }

    function addMessage(text, className) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${className}`;
        messageDiv.innerHTML = text;
        messages.appendChild(messageDiv);
        messages.scrollTop = messages.scrollHeight;
    }

    function removeTyping() {
        const typingMsg = document.querySelector('.typing');
        if (typingMsg) typingMsg.remove();
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    sendBtn.addEventListener('click', sendMessage);
    questionInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            sendMessage();
        }
    });

    questionInput.focus();
});
