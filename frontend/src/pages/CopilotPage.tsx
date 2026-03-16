/**
 * Copilot Page — AI Compliance Copilot chat interface.
 *
 * Features: chat message history, input field, suggested queries,
 * and source citations display.
 */

import { useState } from 'react';

export default function CopilotPage() {
  const [message, setMessage] = useState('');

  const suggestedQueries = [
    'How many submissions are overdue?',
    'What is the current audit readiness score?',
    'List all open CAPAs with Critical priority',
    'When is the next PSUR deadline for Xarelto?',
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 4rem)' }}>
      <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>
        🤖 Compliance Copilot
      </h1>
      <p style={{ color: 'hsl(215 20% 65%)', fontSize: '0.85rem', marginBottom: '1rem' }}>
        Ask questions about submissions, CAPAs, and compliance metrics in natural language.
      </p>

      {/* Suggested queries */}
      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1rem' }}>
        {suggestedQueries.map(q => (
          <button
            key={q}
            onClick={() => setMessage(q)}
            style={{
              padding: '0.35rem 0.75rem',
              borderRadius: 16,
              fontSize: '0.75rem',
              border: '1px solid hsl(217 33% 17%)',
              background: 'transparent',
              color: 'hsl(217 91% 60%)',
              cursor: 'pointer',
            }}
          >
            {q}
          </button>
        ))}
      </div>

      {/* Chat area */}
      <div style={{
        flex: 1,
        backgroundColor: 'hsl(222 47% 8%)',
        borderRadius: 8,
        border: '1px solid hsl(217 33% 17%)',
        padding: '1.25rem',
        overflowY: 'auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        <p style={{ color: 'hsl(215 20% 55%)', fontStyle: 'italic' }}>
          Start a conversation with the Compliance Copilot…
        </p>
      </div>

      {/* Input */}
      <div style={{ display: 'flex', gap: '0.5rem', marginTop: '0.75rem' }}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask the Compliance Copilot…"
          style={{
            flex: 1,
            padding: '0.65rem 1rem',
            borderRadius: 8,
            border: '1px solid hsl(217 33% 17%)',
            backgroundColor: 'hsl(222 47% 8%)',
            color: 'hsl(210 40% 98%)',
            fontSize: '0.85rem',
            outline: 'none',
          }}
        />
        <button style={{
          backgroundColor: 'hsl(217 91% 60%)',
          color: 'white',
          border: 'none',
          borderRadius: 8,
          padding: '0.65rem 1.25rem',
          fontSize: '0.85rem',
          fontWeight: 500,
          cursor: 'pointer',
        }}>
          Send
        </button>
      </div>
    </div>
  );
}
