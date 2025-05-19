import React from 'react';

const Sidebar = ({ 
  isOpen, 
  toggleSidebar, 
  conversations, 
  currentConversationId, 
  onConversationSelect, 
  onNewConversation 
}) => {
  return (
    <>
      {/* Sidebar container */}
      <div className={`sidebar ${!isOpen ? 'sidebar-collapsed' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-title">History</div>
        </div>
        
        <button className="new-chat-button" onClick={onNewConversation}>
          <i className="fas fa-plus"></i> New Chat
        </button>
        
        <div className="conversation-list">
          {conversations.map(conversation => (
            <div 
              key={conversation.id}
              className={`conversation-item ${conversation.id === currentConversationId ? 'active' : ''}`}
              onClick={() => onConversationSelect(conversation.id)}
            >
              <div className="conversation-preview">
                {conversation.preview}
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Separate toggle button that's always visible */}
      <button className="sidebar-toggle" onClick={toggleSidebar}>
        {isOpen ? <i className="fas fa-chevron-left"></i> : <i className="fas fa-chevron-right"></i>}
      </button>
    </>
  );
};

export default Sidebar;