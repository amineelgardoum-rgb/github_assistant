import React, { useState, useEffect, useRef } from "react";
import { askQuestion } from "../api";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "../chatpage.css";

export default function ChatPage({ repoId }) {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hi! How can I help you with this repo?", sources: [] },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userText = input;
    setInput("");
    setLoading(true);
    setMessages((prev) => [...prev, { sender: "user", text: userText }]);

    try {
      const data = await askQuestion(repoId, userText);
      let botText = "";
      const botIndex = messages.length + 1;

      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "", sources: data.sources || [] },
      ]);

      for (let char of data.answer) {
        botText += char;
        setMessages((prev) => {
          const updated = [...prev];
          updated[botIndex] = { ...updated[botIndex], text: botText };
          return updated;
        });
        await new Promise((r) => setTimeout(r, 15));
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "❌ Error fetching answer", sources: [] },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((m, i) => (
          <div key={i} className={`message-row ${m.sender}`}>
            <div className={`bubble ${m.sender}`}>
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  code: ({ children }) => (
                    <code className="chat-code">{children}</code>
                  ),
                }}
              >
                {m.text}
              </ReactMarkdown>

              {m.sender === "bot" && m.sources?.length > 0 && (
                <div className="sources">
                  <strong>Sources:</strong>
                  <ul>
                    {m.sources.map((s, idx) => (
                      <li key={idx}>{s}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="typing">
            <span className="dot" />
            <span className="dot" />
            <span className="dot" />
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <div className="input-bar">
        <input
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask something..."
          disabled={loading}
        />
        <button
          className="send-btn"
          onClick={handleSend}
          disabled={loading || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
}
