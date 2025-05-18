import React from 'react';

const Sidebar = ({ 
    isOpen, 
    conversations, 
    currentConversationId, 
    onConversationSelect, 
    onNewChat 
}) => {
    return (
        <div className={`sidebar ${isOpen ? '' : 'sidebar-collapsed'}`}>
            <div className="sidebar-header">
                <div className="sidebar-title">Conversations</div>
                <button className="new-chat-btn" onClick={onNewChat}>
                    <i className="fas fa-plus"></i> New Chat
                </button>
            </div>
            <div className="conversation-list">
                {conversations.length === 0 ? (
                    <div className="empty-conversations">No conversations yet</div>
                ) : (
                    conversations.map((conv) => (
                        <div 
                            key={conv.id} 
                            className={`conversation-item ${conv.id === currentConversationId ? 'active' : ''}`}
                            onClick={() => onConversationSelect(conv.id)}
                        >
                            <i className="fas fa-comment-dots mr-2"></i> {conv.preview}
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default Sidebar;