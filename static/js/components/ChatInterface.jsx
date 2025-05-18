const ChatInterface = () => {
    const [conversationId, setConversationId] = React.useState(null);
    const [messages, setMessages] = React.useState([]);
    const [isTyping, setIsTyping] = React.useState(false);
    const [error, setError] = React.useState(null);
    
    // Initialize or load conversation
    React.useEffect(() => {
        const fetchConversation = async () => {
            try {
                const response = await axios.get('/api/conversation');
                setConversationId(response.data.id);
                setMessages(response.data.messages || []);
            } catch (err) {
                console.error("Error fetching conversation:", err);
                setError("Failed to load conversation. Please refresh the page.");
            }
        };
        
        fetchConversation();
    }, []);
    
    const handleSendMessage = async (messageText) => {
        if (!messageText.trim()) return;
        
        // Optimistically add user message to the UI
        const userMessage = {
            id: Date.now(),
            text: messageText,
            sender: 'user',
            timestamp: new Date().toISOString()
        };
        
        setMessages(prevMessages => [...prevMessages, userMessage]);
        setIsTyping(true);
        setError(null);
        
        try {
            const response = await axios.post('/api/message', {
                conversation_id: conversationId,
                message: messageText
            });
            
            // Update with the server response
            setMessages(response.data.conversation.messages);
        } catch (err) {
            console.error("Error sending message:", err);
            setError("Failed to get a response. Please try again.");
            
            // Remove the optimistic bot message if there was one
            setMessages(prevMessages => prevMessages.filter(msg => msg.id !== 'temp-bot'));
        } finally {
            setIsTyping(false);
        }
    };
    
    return (
        <div className="chat-container">
            {error && <div className="error-message">{error}</div>}
            <MessageList messages={messages} isTyping={isTyping} />
            <MessageInput onSendMessage={handleSendMessage} isTyping={isTyping} />
        </div>
    );
};
