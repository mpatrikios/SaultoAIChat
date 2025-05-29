import React from 'react';
import ReactMarkdown from 'react-markdown';

const MessageList = ({ messages, isLoading }) => {
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const copyMessageToClipboard = (text) => {
    navigator.clipboard.writeText(text);
  };

  return (
    <div className="message-list">
      {messages.map((message) => (
        <div key={message.id} className={`message ${message.sender}`}>
          <div className="message-content">
            {!message.streaming && (
              <ReactMarkdown
                components={{
                  ul: ({ children }) => (
                    <ul className="markdown-list">{children}</ul>
                  ),
                  ol: ({ children }) => (
                    <ol className="markdown-list">{children}</ol>
                  ),
                  li: ({ children }) => (
                    <li className="markdown-list-item">{children}</li>
                  ),
                  table: ({ children }) => (
                    <div className="table-container">
                      <table className="markdown-table">{children}</table>
                    </div>
                  ),
                }}
              >
                {message.text}
              </ReactMarkdown>
            )}

            {/* Show thinking indicator for streaming messages */}
            {message.streaming && (
              <div className="thinking-indicator">
                <span className="cursor-blink">|</span>
              </div>
            )}

            <div className="message-actions">
              <button 
                className="message-copy-button" 
                onClick={() => copyMessageToClipboard(message.text)}
                title="Copy message to clipboard"
              >
                <i className="fas fa-copy"></i>
              </button>
            </div>
          </div>
          <div className="message-timestamp">
            {formatTimestamp(message.timestamp)}
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="message bot">
          <div className="message-content">
            <div className="thinking-indicator">
              <span className="cursor-blink">Thinking...</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MessageList;