const MessageList = ({ messages, isTyping }) => {
    const messagesEndRef = React.useRef(null);
    
    // Scroll to bottom when messages change or bot is typing
    React.useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, isTyping]);
    
    // Format timestamp
    const formatTime = (isoString) => {
        try {
            const date = new Date(isoString);
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        } catch (e) {
            return '';
        }
    };
    
    if (!messages || messages.length === 0) {
        return (
            <div className="message-list">
                <div className="empty-state">
                    <h2>Welcome to Sumersault Assistant</h2>
                    <p>Ask me anything! I'm here to help you with information, answer questions, or just chat.</p>
                    <div className="example-queries">
                        <div className="example-query" onClick={() => document.querySelector('.message-input').value = "Tell me about sustainable business practices."}>
                            Tell me about sustainable business practices.
                        </div>
                        <div className="example-query" onClick={() => document.querySelector('.message-input').value = "What are the latest trends in digital marketing?"}>
                            What are the latest trends in digital marketing?
                        </div>
                        <div className="example-query" onClick={() => document.querySelector('.message-input').value = "How can I improve team collaboration?"}>
                            How can I improve team collaboration?
                        </div>
                        <div className="example-query" onClick={() => document.querySelector('.message-input').value = "Give me ideas for reducing our carbon footprint."}>
                            Give me ideas for reducing our carbon footprint.
                        </div>
                    </div>
                </div>
                <div ref={messagesEndRef} />
            </div>
        );
    }
    
    return (
        <div className="message-list">
            {messages.map((message) => (
                <div 
                    key={message.id} 
                    className={`message message-${message.sender}`}
                >
                    <div className="message-header">
                        <i className={message.sender === 'user' ? 'fas fa-user' : 'fas fa-robot'}></i>
                        {message.sender === 'user' ? 'You' : 'Sumersault Assistant'}
                    </div>
                    <div className="message-content">{message.text}</div>
                    <div className="message-timestamp">{formatTime(message.timestamp)}</div>
                </div>
            ))}
            
            {isTyping && (
                <div className="typing-indicator">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                </div>
            )}
            
            <div ref={messagesEndRef} />
        </div>
    );
};
