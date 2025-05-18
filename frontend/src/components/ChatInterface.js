import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import Sidebar from './Sidebar';

const ChatInterface = () => {
    const [conversationId, setConversationId] = useState(null);
    const [messages, setMessages] = useState([]);
    const [isTyping, setIsTyping] = useState(false);
    const [error, setError] = useState(null);
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);
    const [conversations, setConversations] = useState([]);
    
    // Initialize or load conversation
    useEffect(() => {
        const initializeChat = async () => {
            await fetchConversation();
            await fetchAllConversations();
        };
        
        initializeChat();
        
        // Set up interval to refresh conversations list every 10 seconds
        const intervalId = setInterval(() => {
            fetchAllConversations();
        }, 10000);
        
        return () => clearInterval(intervalId);
    }, []);
    
    const fetchConversation = async (id = null) => {
        try {
            const url = id ? `/api/conversation?id=${id}` : '/api/conversation';
            const response = await axios.get(url);
            setConversationId(response.data.id);
            setMessages(response.data.messages || []);
        } catch (err) {
            console.error("Error fetching conversation:", err);
            setError("Failed to load conversation. Please refresh the page.");
        }
    };
    
    const fetchAllConversations = async () => {
        try {
            const response = await axios.get('/api/conversations');
            setConversations(response.data);
        } catch (err) {
            console.error("Error fetching conversations:", err);
        }
    };
    
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
            
            // Refresh the conversation list
            fetchAllConversations();
        } catch (err) {
            console.error("Error sending message:", err);
            setError("Failed to get a response. Please try again.");
            
            // Remove the optimistic bot message if there was one
            setMessages(prevMessages => prevMessages.filter(msg => msg.id !== 'temp-bot'));
        } finally {
            setIsTyping(false);
        }
    };
    
    const handleConversationSelect = (id) => {
        if (id !== conversationId) {
            fetchConversation(id);
        }
        
        // On mobile, close the sidebar after selecting
        if (window.innerWidth <= 768) {
            setIsSidebarOpen(false);
        }
    };
    
    const handleNewChat = async () => {
        // Create a new conversation by not passing an ID
        await fetchConversation();
        
        // If we're on mobile, close the sidebar
        if (window.innerWidth <= 768) {
            setIsSidebarOpen(false);
        }
    };
    
    return (
        <div className="main-content">
            <Sidebar 
                isOpen={isSidebarOpen}
                conversations={conversations}
                currentConversationId={conversationId}
                onConversationSelect={handleConversationSelect}
                onNewChat={handleNewChat}
            />
            
            <button 
                className={`toggle-sidebar ${isSidebarOpen ? 'open' : ''}`}
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            >
                <i className={`fas ${isSidebarOpen ? 'fa-chevron-left' : 'fa-bars'}`}></i>
            </button>
            
            <div className={`chat-container ${isSidebarOpen ? 'sidebar-open' : ''}`}>
                {error && <div className="error-message">{error}</div>}
                <MessageList messages={messages} isTyping={isTyping} />
                <MessageInput onSendMessage={handleSendMessage} isTyping={isTyping} />
            </div>
        </div>
    );
};

export default ChatInterface;