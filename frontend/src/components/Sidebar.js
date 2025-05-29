import React from 'react';

const Sidebar = ({ 
  conversations, 
  currentConversationId, 
  onConversationSelect, 
  onNewConversation,
  onDeleteConversation,
  onPinConversation,
  className = ''
}) => {
  return (
    <div className={`sidebar ${className}`}>
      <div className="sidebar-header">
        <div className="sidebar-title">History</div>
      </div>
      
      <button className="new-chat-button" onClick={onNewConversation}>
        <i className="fas fa-plus"></i> New Chat
      </button>
      
      <div className="conversation-list">
        {/* Pinned conversations */}
        {conversations.filter(conv => conv.pinned).length > 0 && (
          <>
            <div className="conversation-section-header">
              <i className="fas fa-thumbtack"></i> Pinned
            </div>
            {conversations.filter(conv => conv.pinned).map(conversation => (
              <div 
                key={conversation.id}
                className={`conversation-item pinned ${conversation.id === currentConversationId ? 'active' : ''}`}
              >
                <div 
                  className="conversation-preview"
                  onClick={() => onConversationSelect(conversation.id)}
                >
                  {conversation.preview}
                </div>
                <div className="conversation-actions">
                  <button 
                    className="pin-conversation-btn pinned"
                    onClick={(e) => {
                      e.stopPropagation();
                      onPinConversation(conversation.id, false);
                    }}
                    title="Unpin conversation"
                  >
                    <i className="fas fa-thumbtack"></i>
                  </button>
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
              </div>
            ))}
          </>
        )}
        
        {/* Regular conversations */}
        {conversations.filter(conv => !conv.pinned).length > 0 && (
          <>
            {conversations.filter(conv => conv.pinned).length > 0 && (
              <div className="conversation-section-header">
                <i className="fas fa-clock"></i> Recent
              </div>
            )}
            {conversations.filter(conv => !conv.pinned).map(conversation => (
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
                <div className="conversation-actions">
                  <button 
                    className="pin-conversation-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      onPinConversation(conversation.id, true);
                    }}
                    title="Pin conversation"
                  >
                    <i className="fas fa-thumbtack"></i>
                  </button>
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
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
};

export default Sidebar;