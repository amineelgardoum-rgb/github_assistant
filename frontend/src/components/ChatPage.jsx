// ChatPage.jsx
import React, { useState, useEffect, useRef, useCallback } from "react";
import { askQuestion } from "../job/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "../style/chatpage.css";

export default function ChatPage({ repoId }) {
  const [messages, setMessages] = useState([
    { 
      id: Date.now(),
      sender: "bot", 
      text: "Hi! How can I help you with this repo?", 
      sources: [],
      timestamp: new Date()
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const streamMessage = useCallback(async (text, messageId) => {
    const words = text.split(' ');
    let currentText = '';
    
    for (let i = 0; i < words.length; i++) {
      currentText += (i > 0 ? ' ' : '') + words[i];
      setMessages(prev => 
        prev.map(m => 
          m.id === messageId 
            ? { ...m, text: currentText }
            : m
        )
      );
      await new Promise(r => setTimeout(r, 30));
    }
  }, []);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userText = input.trim();
    const userMessageId = Date.now();
    const botMessageId = Date.now() + 1;
    
    setInput("");
    setError(null);
    setLoading(true);

    setMessages(prev => [...prev, { 
      id: userMessageId,
      sender: "user", 
      text: userText,
      timestamp: new Date()
    }]);

    try {
      const data = await askQuestion(repoId, userText);
      
      setMessages(prev => [...prev, { 
        id: botMessageId,
        sender: "bot", 
        text: "", 
        sources: data.sources || [],
        timestamp: new Date()
      }]);

      await streamMessage(data.answer, botMessageId);
      
    } catch (err) {
      setError("Failed to get response. Please try again.");
      setMessages(prev => [...prev, { 
        id: botMessageId,
        sender: "bot", 
        text: "❌ Sorry, I encountered an error. Please try again.", 
        sources: [],
        timestamp: new Date(),
        isError: true
      }]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-wrapper">
      <div className="chat-container">
        <div className="chat-header">
          <div className="header-content">
            <div className="status-indicator" />
            <h2>Repository Assistant</h2>
          </div>
          <p className="repo-name">{repoId}</p>
        </div>

        <div className="chat-messages" role="log" aria-live="polite" aria-atomic="false">
          {messages.map((m) => (
            <div key={m.id} className={`message-row ${m.sender}`}>
              <div className={`bubble ${m.sender} ${m.isError ? 'error' : ''}`}>
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code: ({ inline, children }) => 
                      inline ? (
                        <code className="inline-code">{children}</code>
                      ) : (
                        <pre className="code-block">
                          <code>{children}</code>
                        </pre>
                      ),
                    p: ({ children }) => <p className="markdown-p">{children}</p>,
                    ul: ({ children }) => <ul className="markdown-list">{children}</ul>,
                    ol: ({ children }) => <ol className="markdown-list">{children}</ol>,
                  }}
                >
                  {m.text}
                </ReactMarkdown>
                
                {m.sender === "bot" && m.sources?.length > 0 && (
                  <div className="sources">
                    <strong>📁 Sources:</strong>
                    <ul>
                      {m.sources.map((s, idx) => (
                        <li key={idx}>
                          <code>{s}</code>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="message-row bot">
              <div className="typing-indicator">
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {error && (
          <div className="error-banner" role="alert">
            ⚠️ {error}
          </div>
        )}

        <div className="input-bar">
          <div className="input-wrapper">
            <textarea
              ref={inputRef}
              className="chat-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about the repository..."
              disabled={loading}
              rows={1}
              aria-label="Message input"
            />
            <button
              className="send-btn"
              onClick={handleSend}
              disabled={loading || !input.trim()}
              aria-label="Send message"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                <path d="M2 10L18 2L12 18L10 11L2 10Z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}