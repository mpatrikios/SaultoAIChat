import React, { useState, useRef, useEffect } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

const ChatInterface = ({ conversation, isLoading, onSendMessage }) => {
  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const messageAreaRef = useRef();
  
  // Scroll to bottom of message list when new messages arrive
  useEffect(() => {
    if (messageAreaRef.current) {
      messageAreaRef.current.scrollTop = messageAreaRef.current.scrollHeight;
    }
  }, [conversation]);
  
  const handleSendMessage = async (e, file = null) => {
    e.preventDefault();
    
    if ((!inputMessage.trim() && !file) || isSending) return;
    
    const messageText = inputMessage;
    setInputMessage(''); // Clear input immediately
    setIsSending(true);
    
    try {
      await onSendMessage(messageText, file);
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsSending(false);
    }
  };
  
  return (
    <>
      <MessageList 
        messages={conversation?.messages || []} 
        isLoading={isLoading}
        ref={messageAreaRef}
      />
      <MessageInput
        value={inputMessage}
        onChange={(e) => setInputMessage(e.target.value)}
        onSubmit={handleSendMessage}
        disabled={isSending || isLoading}
      />
    </>
  );
};

export default ChatInterface;