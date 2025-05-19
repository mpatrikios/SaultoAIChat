import React, { useState } from 'react';
import DeleteConfirmationModal from './DeleteConfirmationModal';

const Sidebar = ({ 
  conversations, 
  currentConversationId, 
  onConversationSelect, 
  onNewConversation,
  onDeleteConversation
}) => {
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [pendingDeleteId, setPendingDeleteId] = useState(null);
  const [isBulkDelete, setIsBulkDelete] = useState(false);
  
  const handleDeleteClick = (conversationId) => {
    setPendingDeleteId(conversationId);
    setIsBulkDelete(false);
    setIsDeleteModalOpen(true);
  };
  
  const handleBulkDeleteClick = () => {
    setIsBulkDelete(true);
    setIsDeleteModalOpen(true);
  };
  
  const handleConfirmDelete = () => {
    if (isBulkDelete) {
      // Delete all conversations
      conversations.forEach(conv => {
        onDeleteConversation(conv.id);
      });
    } else {
      // Delete single conversation
      onDeleteConversation(pendingDeleteId);
    }
    
    // Close the modal
    setIsDeleteModalOpen(false);
  };

  return (
    <>
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
                  handleDeleteClick(conversation.id);
                }}
                title="Delete conversation"
              >
                <i className="fas fa-trash"></i>
              </button>
            </div>
          ))}
        </div>
        
        {conversations.length > 1 && (
          <button 
            className="clear-all-btn" 
            onClick={handleBulkDeleteClick}
            title="Delete all conversations"
          >
            <i className="fas fa-trash-alt"></i> Clear All
          </button>
        )}
      </div>
      
      <DeleteConfirmationModal 
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        onConfirm={handleConfirmDelete}
        message={isBulkDelete 
          ? "Are you sure you want to delete all conversations? This action cannot be undone."
          : "Are you sure you want to delete this conversation? This action cannot be undone."
        }
      />
    </>
  );
};

export default Sidebar;