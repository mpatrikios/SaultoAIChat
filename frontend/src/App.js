import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import axios from 'axios';

function App() {
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Load all conversations when the app starts
    fetchConversations();
  }, []);

  useEffect(() => {
    // If no conversation is selected and we have conversations, select the first one
    if (!currentConversation && conversations.length > 0) {
      fetchConversation(conversations[0].id);
    }
  }, [conversations, currentConversation]);

  const fetchConversations = async () => {
    try {
      const response = await axios.get('/api/conversations');
      setConversations(response.data);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    }
  };

  const fetchConversation = async (conversationId) => {
    setIsLoading(true);
    try {
      const response = await axios.get(`/api/conversation?id=${conversationId}`);
      setCurrentConversation(response.data);
    } catch (error) {
      console.error('Error fetching conversation:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const createNewConversation = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get('/api/conversation');
      setCurrentConversation(response.data);
      // Refresh the conversation list
      fetchConversations();
    } catch (error) {
      console.error('Error creating new conversation:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async (message) => {
    if (!currentConversation) return;
    
    try {
      const response = await axios.post('/api/message', {
        conversation_id: currentConversation.id,
        message
      });
      
      setCurrentConversation(response.data.conversation);
      // Refresh the conversation list to update previews
      fetchConversations();
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  return (
    <div className="app-container">
      <Sidebar 
        isOpen={isSidebarOpen}
        toggleSidebar={toggleSidebar}
        conversations={conversations}
        currentConversationId={currentConversation?.id}
        onConversationSelect={fetchConversation}
        onNewConversation={createNewConversation}
      />
      
      <div className={`main-content ${!isSidebarOpen ? 'main-content-expanded' : ''}`}>
        <Header 
          title={currentConversation?.id ? `Chat ${currentConversation.id}` : 'New Chat'} 
        />
        
        <ChatInterface 
          conversation={currentConversation}
          isLoading={isLoading}
          onSendMessage={sendMessage}
        />
      </div>
    </div>
  );
}

export default App;