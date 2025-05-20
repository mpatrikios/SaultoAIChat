import React, { useState, useRef } from 'react';

const MessageInput = ({ value, onChange, onSubmit, disabled }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);
  
  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };
  
  const clearSelectedFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (value.trim() || selectedFile) {
      onSubmit(e, selectedFile);
      clearSelectedFile();
    }
  };
  
  const triggerFileInput = () => {
    fileInputRef.current.click();
  };
  
  return (
    <div className="message-input-container">
      {selectedFile && (
        <div className="selected-file">
          <span className="file-name">{selectedFile.name}</span>
          <button 
            type="button" 
            className="remove-file-btn"
            onClick={clearSelectedFile}
          >
            ×
          </button>
        </div>
      )}
      <form className="message-input-form" onSubmit={handleSubmit}>
        <button 
          type="button" 
          className="attach-button"
          onClick={triggerFileInput}
          disabled={disabled}
        >
          <i className="fas fa-paperclip"></i>
        </button>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          disabled={disabled}
        />
        <textarea
          className="message-input"
          placeholder={selectedFile ? "Add a message (optional)" : "Type your message here..."}
          value={value}
          onChange={onChange}
          disabled={disabled}
          onKeyDown={(e) => {
            // Submit form on Enter (without Shift)
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
        />
        <button 
          type="submit" 
          className="send-button"
          disabled={disabled || (!value.trim() && !selectedFile)}
        >
          <i className="fas fa-paper-plane"></i>
        </button>
      </form>
    </div>
  );
};

export default MessageInput;