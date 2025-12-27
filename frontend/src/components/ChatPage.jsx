// ChatPage.jsx with Smart Scrolling, Copy Feature, and Mermaid Support
import React, { useState, useEffect, useRef, useCallback } from "react";
import { askQuestion } from "../job/api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import mermaid from "mermaid";
import "../style/chatpage.css";

// Initialize Mermaid
mermaid.initialize({
  startOnLoad: true,
  theme: 'dark',
  securityLevel: 'loose',
});

// Code block component with copy button and Mermaid support
function CodeBlock({ children, inline, className }) {
  const [copied, setCopied] = useState(false);
  const codeRef = useRef(null);
  const mermaidRef = useRef(null);

  const language = className?.replace('language-', '') || '';
  const isMermaid = language === 'mermaid';

  useEffect(() => {
    if (isMermaid && mermaidRef.current) {
      try {
        mermaid.contentLoaded();
      } catch (error) {
        console.error('Mermaid rendering error:', error);
      }
    }
  }, [isMermaid, children]);

  const handleCopy = async () => {
    const code = codeRef.current?.textContent || String(children);
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  if (inline) {
    return <code className="inline-code">{children}</code>;
  }

  if (isMermaid) {
    return (
      <div className="mermaid-wrapper">
        <button 
          className="copy-button" 
          onClick={handleCopy}
          aria-label="Copy mermaid code"
        >
          {copied ? (
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z"/>
            </svg>
          ) : (
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 010 1.5h-1.5a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-1.5a.75.75 0 011.5 0v1.5A1.75 1.75 0 019.25 16h-7.5A1.75 1.75 0 010 14.25v-7.5z"/>
              <path d="M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0114.25 11h-7.5A1.75 1.75 0 015 9.25v-7.5zm1.75-.25a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-7.5a.25.25 0 00-.25-.25h-7.5z"/>
            </svg>
          )}
          <span>{copied ? 'Copied!' : 'Copy'}</span>
        </button>
        <div 
          ref={mermaidRef} 
          className="mermaid"
          style={{ display: 'none' }}
        >
          <span ref={codeRef}>{String(children)}</span>
        </div>
        <div 
          ref={mermaidRef}
          className="mermaid"
        >
          {String(children)}
        </div>
      </div>
    );
  }

  return (
    <div className="code-block-wrapper">
      <button 
        className="copy-button" 
        onClick={handleCopy}
        aria-label="Copy code"
      >
        {copied ? (
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z"/>
          </svg>
        ) : (
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
            <path d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 010 1.5h-1.5a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-1.5a.75.75 0 011.5 0v1.5A1.75 1.75 0 019.25 16h-7.5A1.75 1.75 0 010 14.25v-7.5z"/>
            <path d="M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0114.25 11h-7.5A1.75 1.75 0 015 9.25v-7.5zm1.75-.25a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-7.5a.25.25 0 00-.25-.25h-7.5z"/>
          </svg>
        )}
        <span>{copied ? 'Copied!' : 'Copy'}</span>
      </button>
      <pre className="code-block">
        <code ref={codeRef}>{children}</code>
      </pre>
    </div>
  );
}

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
  const [autoScroll, setAutoScroll] = useState(true);
  const [userHasScrolled, setUserHasScrolled] = useState(false);
  
  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const scrollTimeoutRef = useRef(null);

  // Check if user is near bottom of chat
  const isNearBottom = useCallback(() => {
    const container = messagesContainerRef.current;
    if (!container) return true;
    
    const threshold = 100; // pixels from bottom
    const position = container.scrollHeight - container.scrollTop - container.clientHeight;
    return position < threshold;
  }, []);

  // Handle scroll - only disable auto-scroll if user manually scrolls
  const handleScroll = useCallback(() => {
    if (scrollTimeoutRef.current) {
      clearTimeout(scrollTimeoutRef.current);
    }
    
    // Debounce scroll check to avoid interference during auto-scroll
    scrollTimeoutRef.current = setTimeout(() => {
      const nearBottom = isNearBottom();
      
      // Only update if user scrolled away from bottom
      if (!nearBottom && !userHasScrolled) {
        setUserHasScrolled(true);
        setAutoScroll(false);
      } else if (nearBottom && userHasScrolled) {
        setUserHasScrolled(false);
        setAutoScroll(true);
      }
    }, 150);
  }, [isNearBottom, userHasScrolled]);

  // Auto-scroll only if enabled
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
    setAutoScroll(true); // Re-enable auto-scroll for new message
    setUserHasScrolled(false); // Reset scroll state

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

  // Scroll to bottom button
  const scrollToBottom = () => {
    setAutoScroll(true);
    setUserHasScrolled(false);
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
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

        <div 
          className="chat-messages" 
          ref={messagesContainerRef}
          onScroll={handleScroll}
          role="log" 
          aria-live="polite" 
          aria-atomic="false"
        >
          {messages.map((m) => (
            <div key={m.id} className={`message-row ${m.sender}`}>
              <div className={`bubble ${m.sender} ${m.isError ? 'error' : ''}`}>
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code: ({ inline, className, children }) => (
                      <CodeBlock inline={inline} className={className}>{children}</CodeBlock>
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

        {/* Scroll to bottom button - shows when not auto-scrolling */}
        {!autoScroll && (
          <button 
            className="scroll-to-bottom"
            onClick={scrollToBottom}
            aria-label="Scroll to bottom"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path d="M10 14L5 9H15L10 14Z" />
            </svg>
          </button>
        )}

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