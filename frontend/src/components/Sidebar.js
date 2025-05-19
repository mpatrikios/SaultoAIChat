import React from 'react';

const Sidebar = ({ 
  conversations, 
  currentConversationId, 
  onConversationSelect, 
  onNewConversation,
  onDeleteConversation
}) => {
  return (
    <div className="sidebar">
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
          >
            <div 
              className="conversation-preview"
              onClick={() => onConversationSelect(conversation.id)}
            >
              {conversation.preview}
            </div>
            <button 
              className="delete-conversation-btn"
              onClick={(e) => {
                e.stopPropagation();
                onDeleteConversation(conversation.id);
              }}
              title="Delete conversation"
            >
              <i className="fas fa-trash"></i>
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Sidebar;