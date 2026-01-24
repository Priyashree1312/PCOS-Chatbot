// static/js/chat.js - PCOS Pinky FULL VERSION
document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("question") || document.getElementById("message-input");
    const sendBtn = document.getElementById("sendBtn") || document.getElementById("send-btn");
    const chatMessages = document.getElementById("messages") || document.getElementById("chat-messages") || document.getElementById("chatContainer");
    const remindersContainer = document.getElementById('remindersContainer');

    // Your daily suggestions (KEEPING YOUR FEATURE!)
    const dailySuggestions = [
        "💧 Drink at least 2L of water",
        "🥗 Eat a high-fiber breakfast", 
        "🏃‍♀️ 30 min exercise",
        "📅 Track your period",
        "🛌 Sleep 7-8 hours"
    ];

    // Show reminders (YOUR FEATURE!)
    if (remindersContainer) {
        dailySuggestions.forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'reminder-item';
            item.textContent = suggestion;
            item.addEventListener('click', () => appendMessage("You", suggestion));
            remindersContainer.appendChild(item);
        });
    }

    function appendMessage(sender, text) {
        const msgDiv = document.createElement("div");
        msgDiv.classList.add("message", sender === "You" ? "user-message" : "bot-message");
        msgDiv.innerHTML = text.replace(/\n/g, '<br>');
        chatMessages.appendChild(msgDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        // 💖 YOUR HEART ANIMATION + PINK MAGIC
        if (sender !== "You") createHeart();
    }

    // MAIN SEND FUNCTION (YOUR FEATURES + PINKY STYLE)
    async function sendMessage() {
        const message = input.value.trim();
        if (!message) return;

        // User message
        appendMessage("You", message);
        input.value = "";

        // 💕 PINKY THINKING ANIMATION (YOUR STYLE)
        sendBtn.innerHTML = '💕 Pinky is thinking...';
        sendBtn.classList.add('loading');

        // Typing dots (YOUR FEATURE!)
        const typingBubble = document.createElement('div');
        typingBubble.className = 'typing';
        typingBubble.innerHTML = '<div class="dot"></div><div class="dot"></div><div class="dot"></div>';
        chatMessages.appendChild(typingBubble);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const response = await fetch('/chat/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ question: message })
            });

            const data = await response.json();
            typingBubble.remove();

            // YOUR FEATURES: Emojis, Diet Charts, Collapsible Tips!
            let botText = data.answer || data.response || '🌸 Ask me about PCOS!';
            botText = addEmojis(botText);  // YOUR EMOJI MAGIC!
            appendMessage("Bot", botText);

            // YOUR COLLAPSIBLE TIPS FEATURE
            if (data.tips && data.tips.length > 0) {
                data.tips.forEach(tip => addCollapsibleTip(tip.title, tip.content));
            }

        } catch (error) {
            typingBubble.remove();
            appendMessage("Bot", "🌩️ Oops lovely! Try again 💕");
        }

        sendBtn.innerHTML = '✨ Ask Pinky';
        sendBtn.classList.remove('loading');
        input.focus();
    }

    // YOUR FEATURES: Auto-emojis!
    function addEmojis(text) {
        const emojiMap = {
            'diet': '🥗', 'exercise': '🏃‍♀️', 'weight': '⚖️',
            'symptom': '🩺', 'PCOS': '🌸', 'doctor': '👩‍⚕️',
            'period': '📅', 'treatment': '💊', 'yoga': '🧘‍♀️'
        };
        for (const key in emojiMap) {
            const regex = new RegExp(`\\b${key}\\b`, 'gi');
            text = text.replace(regex, `${emojiMap[key]} $&`);
        }
        return text;
    }

    // YOUR COLLAPSIBLE TIPS FEATURE
    function addCollapsibleTip(title, content) {
        const coll = document.createElement('div');
        coll.className = 'collapsible';
        coll.innerHTML = `💡 ${title}`;

        const collContent = document.createElement('div');
        collContent.className = 'collapsible-content';
        collContent.innerHTML = content;

        coll.addEventListener('click', () => {
            collContent.style.display = collContent.style.display === 'block' ? 'none' : 'block';
        });

        chatMessages.appendChild(coll);
        chatMessages.appendChild(collContent);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // 💖 YOUR HEART ANIMATION
    function createHeart() {
        const heart = document.createElement('div');
        heart.innerHTML = '💖';
        heart.style.cssText = `
            position: fixed; right: 20px; top: 20px; 
            font-size: 30px; pointer-events: none;
            animation: heartFloat 3s ease-out forwards;
            z-index: 1000;
        `;
        document.body.appendChild(heart);
        setTimeout(() => heart.remove(), 3000);
    }

    // YOUR CSRF HELPER
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.startsWith(name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // EVENT LISTENERS (BOTH YOUR STYLES)
    sendBtn.addEventListener("click", sendMessage);
    input.addEventListener("keypress", function(e) {
        if (e.key === "Enter") {
            sendBtn.click();
            e.preventDefault();
        }
    });
});
