const MessageInput = ({ onSendMessage, isTyping }) => {
    const [message, setMessage] = React.useState('');
    const textareaRef = React.useRef(null);
    
    const handleSubmit = (e) => {
        e.preventDefault();
        if (message.trim() && !isTyping) {
            onSendMessage(message);
            setMessage('');
            
            // Reset textarea height
            if (textareaRef.current) {
                textareaRef.current.style.height = 'auto';
            }
        }
    };
    
    const handleKeyDown = (e) => {
        // Submit on Enter (without Shift)
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };
    
    // Auto-resize textarea based on content
    const handleTextareaChange = (e) => {
        const textarea = e.target;
        setMessage(textarea.value);
        
        // Reset height to properly calculate scroll height
        textarea.style.height = 'auto';
        
        // Set new height based on content (with max height)
        const newHeight = Math.min(textarea.scrollHeight, 150);
        textarea.style.height = `${newHeight}px`;
    };
    
    return (
        <div className="message-input-container">
            <form className="message-input-form" onSubmit={handleSubmit}>
                <textarea
                    ref={textareaRef}
                    className="message-input"
                    value={message}
                    onChange={handleTextareaChange}
                    onKeyDown={handleKeyDown}
                    placeholder="Type your message here..."
                    rows="1"
                    disabled={isTyping}
                ></textarea>
                <button 
                    type="submit" 
                    className="send-button"
                    disabled={!message.trim() || isTyping}
                >
                    <i className="fas fa-paper-plane"></i>
                </button>
            </form>
        </div>
    );
};
