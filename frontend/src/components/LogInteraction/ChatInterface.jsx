import { useState, useRef, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { sendMessage, addUserMessage, clearChat, resetDraftForm } from '../../store/slices/chatSlice.js';
import { Trash2, ChevronRight } from 'lucide-react';

const SUGGESTIONS = [
  "Today I met with Dr. Smith and discussed product CardioGuard XR efficiency. The sentiment was positive and I shared the brochures.",
  "Sorry, the name was actually Dr. John and the sentiment was negative.",
  "Search Dr. Sarah Chen",
  "Prepare talking points for Dr Emily Patel",
  "Recommend products for Dr Aisha Khan",
  "Generate follow-up email for Dr James Rodriguez",
];

export default function ChatInterface() {
  const dispatch = useDispatch();
  const { messages, loading } = useSelector((s) => s.chat);
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = () => {
    if (!input.trim() || loading) return;
    const msg = input.trim();
    setInput('');
    dispatch(addUserMessage(msg));
    dispatch(sendMessage({
      message: msg,
      conversationHistory: messages,
    }));
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSuggestion = (suggestion) => {
    setInput(suggestion);
    inputRef.current?.focus();
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      background: '#ffffff',
      fontFamily: 'Inter, system-ui, sans-serif'
    }}>
      {/* Header */}
      <div style={{
        padding: '16px 20px',
        borderBottom: '1px solid #dee2e6',
        display: 'flex',
        alignItems: 'center',
        gap: '10px'
      }}>
        <div style={{ fontSize: '1.25rem' }}>🤖</div>
        <div>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#0d6efd', margin: 0 }}>
            AI Assistant
          </h3>
          <p style={{ fontSize: '0.78rem', color: '#6c757d', margin: '2px 0 0 0' }}>
            Log Interaction details here via chat
          </p>
        </div>
      </div>

      {/* Messages Scroll Area */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px'
      }}>
        {/* Cyan instruction bubble when empty */}
        {messages.length === 0 && (
          <div style={{
            background: '#e0f2fe',
            borderLeft: '4px solid #0284c7',
            borderRadius: '6px',
            padding: '12px 16px',
            fontSize: '0.85rem',
            color: '#0369a1',
            lineHeight: '1.4'
          }}>
            Log interaction details here (e.g., "Met Dr. Smith, discussed Prodo-X efficacy, positive sentiment, shared brochure") or ask for help.
          </div>
        )}

        {/* Suggestions when empty */}
        {messages.length === 0 && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 700, color: '#868e96', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Select a scenario:
            </div>
            {SUGGESTIONS.map((s, i) => (
              <button
                key={i}
                onClick={() => handleSuggestion(s)}
                style={{
                  textAlign: 'left',
                  background: '#ffffff',
                  border: '1px solid #dee2e6',
                  borderRadius: '6px',
                  padding: '8px 12px',
                  fontSize: '0.8rem',
                  color: '#495057',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  transition: 'background 0.15s ease'
                }}
                onMouseOver={(e) => e.currentTarget.style.background = '#f8f9fa'}
                onMouseOut={(e) => e.currentTarget.style.background = '#ffffff'}
              >
                <ChevronRight size={12} color="#0d6efd" />
                {s}
              </button>
            ))}
          </div>
        )}

        {/* Message List */}
        {messages.map((msg, idx) => {
          const isUser = msg.role === 'user';
          return (
            <div
              key={idx}
              style={{
                alignSelf: 'stretch',
                display: 'flex',
                flexDirection: 'column',
                gap: '4px'
              }}
            >
              <div style={{
                background: isUser ? '#f8f9fa' : '#e8f5e9',
                border: '1px solid',
                borderColor: isUser ? '#dee2e6' : '#c8e6c9',
                borderLeft: '4px solid',
                borderLeftColor: isUser ? '#0d6efd' : '#4caf50',
                borderRadius: '6px',
                padding: '12px 16px',
                fontSize: '0.88rem',
                color: '#212529',
                lineHeight: '1.45',
                boxShadow: '0 1px 2px rgba(0,0,0,0.02)'
              }}>
                {msg.content.split('\n').map((line, i) => (
                  <span key={i}>{line}<br /></span>
                ))}
              </div>
            </div>
          );
        })}

        {/* Typing Loader */}
        {loading && (
          <div style={{
            alignSelf: 'flex-start',
            background: '#f8f9fa',
            border: '1px solid #dee2e6',
            borderLeft: '4px solid #4caf50',
            borderRadius: '6px',
            padding: '10px 16px',
            display: 'flex',
            alignItems: 'center',
            gap: '4px'
          }}>
            <div style={{ width: '6px', height: '6px', background: '#868e96', borderRadius: '50%', animation: 'bounce 1.4s infinite ease-in-out both' }} />
            <div style={{ width: '6px', height: '6px', background: '#868e96', borderRadius: '50%', animation: 'bounce 1.4s infinite ease-in-out both 0.2s' }} />
            <div style={{ width: '6px', height: '6px', background: '#868e96', borderRadius: '50%', animation: 'bounce 1.4s infinite ease-in-out both 0.4s' }} />
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Footer / Input Area */}
      <div style={{
        padding: '16px 20px',
        borderTop: '1px solid #dee2e6',
        background: '#ffffff',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px'
      }}>
        {messages.length > 0 && (
          <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button
              onClick={() => {
                dispatch(clearChat());
                dispatch(resetDraftForm());
              }}
              style={{
                background: 'none',
                border: 'none',
                color: '#6c757d',
                fontSize: '0.78rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontWeight: 500
              }}
            >
              <Trash2 size={12} /> Clear Chat
            </button>
          </div>
        )}

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <textarea
            ref={inputRef}
            style={{
              flex: 1,
              padding: '12px 16px',
              fontSize: '0.88rem',
              border: '1px solid #ced4da',
              borderRadius: '24px',
              background: '#ffffff',
              color: '#212529',
              resize: 'none',
              height: '52px',
              lineHeight: '1.4',
              outline: 'none',
            }}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe Interaction..."
            rows={1}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || loading}
            style={{
              background: '#0d6efd',
              color: '#ffffff',
              borderRadius: '24px',
              border: 'none',
              fontSize: '0.85rem',
              fontWeight: 700,
              lineHeight: '1.2',
              textAlign: 'center',
              cursor: (!input.trim() || loading) ? 'not-allowed' : 'pointer',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              width: '60px',
              height: '52px',
              opacity: (!input.trim() || loading) ? 0.65 : 1,
              transition: 'opacity 0.2s ease',
              boxShadow: '0 4px 6px rgba(13, 110, 253, 0.15)'
            }}
          >
            <span>A</span>
            <span>Log</span>
          </button>
        </div>
      </div>
    </div>
  );
}
