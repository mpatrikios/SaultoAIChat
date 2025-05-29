import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ChatInterface from './components/ChatInterface';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import './styles/style.css';

function App() {
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState(false);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const response = await axios.get('/api/conversations');
      setConversations(response.data);
    } catch (error) {
      console.error('Error loading conversations:', error);
    }
  };

  const handleSendMessage = async (message, file = null) => {
    if (!currentConversation) {
      // Create new conversation if none exists
      try {
        const response = await axios.get('/api/conversation');
        setCurrentConversation(response.data);
      } catch (error) {
        console.error('Error creating conversation:', error);
        return;
      }
    }

    setIsLoading(true);

    try {
      const formData = new FormData();
      formData.append('conversation_id', currentConversation.id);
      formData.append('message', message);
      if (file) {
        formData.append('file', file);
      }

      const response = await axios.post('/api/message', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setCurrentConversation(response.data.conversation);
      await loadConversations();
    } catch (error) {
      console.error('Error sending message:', error);
      // Show error in the UI instead of fallback
      setCurrentConversation(prev => ({
        ...prev,
        messages: [...prev.messages, {
          id: Date.now().toString(),
          text: 'Sorry, I encountered an error. Please try again.',
          sender: 'bot',
          timestamp: new Date().toISOString()
        }]
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const toggleMobileSidebar = () => {
    setIsMobileSidebarOpen(!isMobileSidebarOpen);
  };

  const closeMobileSidebar = () => {
    setIsMobileSidebarOpen(false);
  };

  return (
    <div className="app-container">
      {/* Mobile overlay */}
      <div 
        className={`mobile-sidebar-overlay ${isMobileSidebarOpen ? 'active' : ''}`}
        onClick={closeMobileSidebar}
      ></div>
      
      <Header onMobileMenuToggle={toggleMobileSidebar} />
      
      <div className="main-content">
        <Sidebar 
          conversations={conversations}
          currentConversation={currentConversation}
          onSelectConversation={(conversation) => {
            setCurrentConversation(conversation);
            closeMobileSidebar();
          }}
          onNewConversation={() => {
            setCurrentConversation(null);
            closeMobileSidebar();
          }}
          className={isMobileSidebarOpen ? 'mobile-open' : ''}
        />
        <ChatInterface
          conversation={currentConversation}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}

export default App;