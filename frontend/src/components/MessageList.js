import React, { forwardRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import rehypeSanitize from "rehype-sanitize";
import rehypeHighlight from "rehype-highlight";

const MessageList = forwardRef(({ messages, isLoading }, ref) => {
  const formatTimestamp = (timestamp) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch (e) {
      return "";
    }
  };

  return (
    <div className="message-area" ref={ref}>
      {messages.length === 0 && !isLoading && (
        <div className="empty-chat-message">
          <p>No messages yet. Start a conversation!</p>
        </div>
      )}

      {messages.map((message) => (
        <div key={message.id} className={`message ${message.sender}`}>
          <div className="message-content">
            {message.sender === "user" ? (
              message.text
            ) : (
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeRaw, rehypeSanitize, rehypeHighlight]}
                components={{
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || "");
                    return !inline && match ? (
                      <div className="code-block-wrapper">
                        <div className="code-block-header">
                          <span>{match[1]}</span>
                        </div>
                        <pre className={className}>
                          <code className={className} {...props}>
                            {children}
                          </code>
                        </pre>
                      </div>
                    ) : (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    );
                  },
                  pre: ({ children }) => (
                    <pre className="markdown-pre">{children}</pre>
                  ),
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
          </div>
          <div className="message-timestamp">
            {formatTimestamp(message.timestamp)}
          </div>
        </div>
      ))}

      {isLoading && (
        <div className="message bot typing-message">
          <div className="message-content">
            <div className="typing-indicator">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
});

export default MessageList;
