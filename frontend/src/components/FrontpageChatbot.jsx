import React, { useState, useRef, useEffect } from 'react';
import {
  MessageSquare,
  Send,
  Sparkles,
  Bot,
  User,
  Trash2,
  X,
  Minus,
  Maximize2
} from 'lucide-react';
import { queryAgent } from '../services/api';

export default function FrontpageChatbot({ dataset, onLoadSample, isOpen: propIsOpen, onToggle }) {
  const [internalOpen, setInternalOpen] = useState(false);
  const isOpen = propIsOpen !== undefined ? propIsOpen : internalOpen;

  const toggleOpen = (val) => {
    const next = typeof val === 'boolean' ? val : !isOpen;
    setInternalOpen(next);
    if (onToggle) onToggle(next);
  };

  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'agent',
      text: "👋 **Hi! I'm DataSense AI Assistant.**\n\nI can analyze your dataset, compute statistics, generate distribution plots, and answer any data queries. Ask me anything or click a suggestion below!",
      time: 'Just now',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      scrollToBottom();
    }
  }, [messages, loading, isOpen]);

  // When a dataset is loaded or updated, notify in chat
  useEffect(() => {
    if (dataset?.filename) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          sender: 'agent',
          text: `📁 **Dataset Attached:** \`${dataset.filename}\` (${dataset.shape[0]} rows, ${dataset.shape[1]} columns). You can ask me about averages, correlations, missing values, or highest/lowest records!`,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    }
  }, [dataset?.dataset_id]);

  const handleSend = async (queryText) => {
    const textToSend = (queryText || input).trim();
    if (!textToSend || loading) return;

    const userMsg = {
      id: Date.now(),
      sender: 'user',
      text: textToSend,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await queryAgent(textToSend, dataset?.dataset_id);
      const agentMsg = {
        id: Date.now() + 1,
        sender: 'agent',
        text: res.response || 'No answer returned from analysis engine.',
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, agentMsg]);
    } catch (err) {
      const errorMsg = {
        id: Date.now() + 1,
        sender: 'agent',
        text: `⚠️ **Error:** ${err.message || 'Could not communicate with agent.'}`,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => {
    setMessages([
      {
        id: Date.now(),
        sender: 'agent',
        text: 'Chat history cleared. How can I help you with your data today?',
        time: 'Just now',
      },
    ]);
  };

  const quickPrompts = dataset ? [
    'What is the summary of this data?',
    'Are there any missing or null values?',
    'What are the averages of numeric features?',
    'Which columns have highest correlation?',
    'List all available columns'
  ] : [
    'What can DataSense AI do?',
    'How do I upload and clean data?',
    'What charts are generated automatically?',
    'Load sample sales dataset'
  ];

  const handleQuickPromptClick = (prompt) => {
    if (prompt === 'Load sample sales dataset' && onLoadSample) {
      onLoadSample();
      return;
    }
    handleSend(prompt);
  };

  return (
    <div className="floating-chatbot-container" id="floating-chatbot">
      {/* 1. Floating Chat Window (When Open) */}
      {isOpen && (
        <div className="floating-chat-window">
          {/* Header */}
          <div className="floating-chat-header">
            <div className="floating-header-info">
              <div className="floating-avatar-box">
                <Bot className="w-5 h-5 text-primary" />
                <span className="online-indicator"></span>
              </div>
              <div>
                <h4 className="floating-title">DataSense AI</h4>
                <p className="floating-subtitle">
                  {dataset ? `Connected: ${dataset.filename}` : 'Autonomous Agent'}
                </p>
              </div>
            </div>

            <div className="floating-header-actions">
              <button
                className="chat-action-btn"
                onClick={clearChat}
                title="Clear Chat History"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
              <button
                className="chat-action-btn close-btn"
                onClick={() => toggleOpen(false)}
                title="Close Chat"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Quick Prompts Bar */}
          <div className="floating-quick-prompts">
            <div className="quick-prompts-scroll">
              {quickPrompts.map((prompt, i) => (
                <button
                  key={i}
                  className="floating-prompt-chip"
                  onClick={() => handleQuickPromptClick(prompt)}
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>

          {/* Messages Area */}
          <div className="floating-messages-area">
            {messages.map((m) => (
              <div key={m.id} className={`floating-msg-row ${m.sender}`}>
                <div className="floating-msg-bubble">
                  <div className="floating-msg-sender">
                    {m.sender === 'agent' ? '🤖 DataSense' : '👤 You'}
                    <span className="floating-msg-time">{m.time}</span>
                  </div>
                  <div className="floating-msg-text">{m.text}</div>
                </div>
              </div>
            ))}

            {loading && (
              <div className="floating-msg-row agent">
                <div className="floating-msg-bubble thinking">
                  <div className="chat-typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Bar */}
          <form
            className="floating-input-form"
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
          >
            <input
              type="text"
              className="floating-input"
              placeholder={
                dataset
                  ? `Ask about ${dataset.filename}...`
                  : 'Ask about data analysis or features...'
              }
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
              autoFocus
            />
            <button
              type="submit"
              className="btn btn-primary floating-send-btn"
              disabled={!input.trim() || loading}
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      )}

      {/* 2. Floating Action Button (FAB) in the Bottom-Right Corner */}
      <button
        type="button"
        className={`floating-fab-btn ${isOpen ? 'active' : ''}`}
        onClick={() => toggleOpen(!isOpen)}
        title={isOpen ? 'Close Chat' : 'Chat with DataSense AI'}
        aria-label="Toggle AI Chatbot"
      >
        {isOpen ? (
          <X className="w-6 h-6 text-white" />
        ) : (
          <>
            <Bot className="w-6 h-6 text-white" />
            <span className="fab-online-badge"></span>
          </>
        )}
      </button>
    </div>
  );
}
