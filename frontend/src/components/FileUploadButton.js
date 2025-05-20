import React, { useRef } from 'react';

const FileUploadButton = ({ onFileSelect, disabled }) => {
  const fileInputRef = useRef(null);
  
  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      onFileSelect(e.target.files[0]);
    }
  };
  
  const triggerFileInput = () => {
    fileInputRef.current.click();
  };
  
  return (
    <div className="file-upload-container">
      <button 
        type="button" 
        className="file-upload-button"
        onClick={triggerFileInput}
        disabled={disabled}
        title="Attach a file"
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
    </div>
  );
};

export default FileUploadButton;