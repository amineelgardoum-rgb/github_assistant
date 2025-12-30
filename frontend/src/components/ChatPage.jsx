// ChatPage.jsx
import React, { useState, useEffect, useRef, useCallback } from "react";
import { askQuestion } from "../job/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "../style/chatpage.css";

export default function ChatPage({ repoId }) {
  const generateId = useCallback(() => {
    if (typeof window !== "undefined" && window.crypto && window.crypto.randomUUID) {
      return window.crypto.randomUUID();
    }
    return `msg-${Date.now()}-${Math.random().toString(36).substring(2, 11)}`;
  }, []);

  const [messages, setMessages] = useState([
    { 
      id: "initial-message",
      sender: "bot", 
      text: "Hi! How can I help you with this repo?", 
      sources: [],
      timestamp: new Date()
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const [userHasScrolled, setUserHasScrolled] = useState(false);
  
  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const scrollTimeoutRef = useRef(null);

  const isNearBottom = useCallback(() => {
    const container = messagesContainerRef.current;
    if (!container) return true;
    const threshold = 100;
    const position = container.scrollHeight - container.scrollTop - container.clientHeight;
    return position < threshold;
  }, []);

  const handleScroll = useCallback(() => {
    if (scrollTimeoutRef.current) clearTimeout(scrollTimeoutRef.current);
    
    scrollTimeoutRef.current = setTimeout(() => {
      const nearBottom = isNearBottom();
      if (!nearBottom && !userHasScrolled) {
        setUserHasScrolled(true);
        setAutoScroll(false);
      } else if (nearBottom && userHasScrolled) {
        setUserHasScrolled(false);
        setAutoScroll(true);
      }
    }, 150);
  }, [isNearBottom, userHasScrolled]);

  useEffect(() => {
    if (autoScroll) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, loading, autoScroll]);

  const streamMessage = useCallback(async (text, messageId) => {
    const words = text.split(' ');
    let currentText = '';
    
    for (let i = 0; i < words.length; i++) {
      currentText += (i > 0 ? ' ' : '') + words[i];
      setMessages(prev => 
        prev.map(m => m.id === messageId ? { ...m, text: currentText } : m)
      );
      await new Promise(r => setTimeout(r, 20));
    }
  }, []);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userText = input.trim();
    const userMessageId = generateId();
    const botMessageId = generateId();
    
    setInput("");
    setError(null);
    setLoading(true);
    setAutoScroll(true);
    setUserHasScrolled(false);

    setMessages(prev => [...prev, { 
      id: userMessageId,
      sender: "user", 
      text: userText,
      timestamp: new Date()
    }]);

    try {
      const data = await askQuestion(repoId, userText);
      
      const answerText = typeof data.answer === 'string' 
        ? data.answer 
        : data.answer?.content || "No response received";
      
      setMessages(prev => [...prev, { 
        id: botMessageId,
        sender: "bot", 
        text: "", 
        sources: data.sources || [],
        timestamp: new Date()
      }]);

      await streamMessage(answerText, botMessageId);
      
    } catch (err) {
      console.error("Error getting response:", err);
      setError("Failed to get response. Please try again.");
      setMessages(prev => [...prev, { 
        id: generateId(),
        sender: "bot", 
        text: "❌ Sorry, I encountered an error. Please try again.", 
        sources: [],
        timestamp: new Date(),
        isError: true
      }]);
    } finally {
      setLoading(false);
      setTimeout(() => inputRef.current?.focus(), 0);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const scrollToBottom = () => {
    setAutoScroll(true);
    setUserHasScrolled(false);
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="chat-wrapper">
      <div className="chat-container">
        {/* Header */}
        <div className="chat-header">
          <div className="header-content">
            <div className="status-indicator" />
            <h2>Repository Assistant</h2>
          </div>
          <p className="repo-name">📦 {repoId}</p>
        </div>

        {/* Messages */}
        <div 
          className="chat-messages" 
          ref={messagesContainerRef}
          onScroll={handleScroll}
          role="log" 
          aria-live="polite"
        >
          {messages.map((m) => (
            <div key={m.id} className={`message-row ${m.sender}`}>
              <div className="message-wrapper">
                <div className={`bubble ${m.sender} ${m.isError ? 'error' : ''}`}>
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      p: ({children}) => <p className="markdown-p">{children}</p>,
                      code: ({inline, children}) => (
                        <code className={inline ? 'inline-code' : 'block-code'}>
                          {children}
                        </code>
                      )
                    }}
                  >
                    {m.text}
                  </ReactMarkdown>
                  
                  {m.sender === "bot" && m.sources?.length > 0 && (
                    <div className="sources">
                      <strong className="sources-title">📁 Sources</strong>
                      <ul className="sources-list">
                        {m.sources.map((s, idx) => (
                          <li key={`${m.id}-src-${idx}`}>
                            <code className="source-code">{s}</code>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
                
                <div className="timestamp">
                  {m.timestamp.toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}
                </div>
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

        {/* Scroll to bottom button */}
        {!autoScroll && (
          <button 
            className="scroll-to-bottom"
            onClick={scrollToBottom}
            aria-label="Scroll to bottom"
          >
            <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 16L6 10H18L12 16Z" />
            </svg>
          </button>
        )}

        {/* Error banner */}
        {error && (
          <div className="error-banner" role="alert">
            ⚠️ {error}
          </div>
        )}

        {/* Input bar */}
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