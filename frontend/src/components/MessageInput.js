import React from 'react';

const MessageInput = ({ value, onChange, onSubmit, disabled }) => {
  return (
    <div className="message-input-container">
      <form className="message-input-form" onSubmit={onSubmit}>
        <textarea
          className="message-input"
          placeholder="Type your message here..."
          value={value}
          onChange={onChange}
          disabled={disabled}
          onKeyDown={(e) => {
            // Submit form on Enter (without Shift)
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              onSubmit(e);
            }
          }}
        />
        <button 
          type="submit" 
          className="send-button"
          disabled={disabled || !value.trim()}
        >
          <i className="fas fa-paper-plane"></i>
        </button>
      </form>
    </div>
  );
};

export default MessageInput;