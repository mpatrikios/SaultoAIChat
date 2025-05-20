import React, { useState } from 'react';
import FileUploadButton from './FileUploadButton';

const MessageInput = ({ value, onChange, onSubmit, disabled }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  
  const handleFileSelect = (file) => {
    setSelectedFile(file);
  };
  
  const clearSelectedFile = () => {
    setSelectedFile(null);
  };
  
  const handleSubmit = (e) => {
    e.preventDefault();
    if (value.trim() || selectedFile) {
      onSubmit(e, selectedFile);
      clearSelectedFile();
    }
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
        <FileUploadButton 
          onFileSelect={handleFileSelect}
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