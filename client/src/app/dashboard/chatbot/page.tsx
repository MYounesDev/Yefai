'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Plus, MessageSquare, Bot, User, ExternalLink, Sparkles } from 'lucide-react';
import { mockChatSessions, mockInitialMessages, getMockResponse } from '@/services/mock/chat';
import { cn, formatRelativeTime } from '@/lib/utils';
import type { ChatMessage, ChatSession } from '@/types';

const SUGGESTED_PROMPTS = [
  'Which tools have the highest wear right now?',
  'Show me spare parts at crisis level',
  'What anomalies were detected in the last 24h?',
  'Compare wear rates across the fleet',
];

function MessageBubble({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === 'user';
  const isSystem = msg.role === 'system';

  if (isSystem) {
    return (
      <div className="flex justify-center">
        <span className="text-[11px] text-muted px-3 py-1 rounded-full bg-surface-2 border border-border">
          {msg.content}
        </span>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn('flex gap-3', isUser ? 'flex-row-reverse' : 'flex-row')}
    >
      {/* Avatar */}
      <div className={cn(
        'w-7 h-7 rounded-full flex items-center justify-center shrink-0 mt-0.5',
        isUser ? 'bg-gradient-to-br from-cyan-500 to-violet-600' : 'bg-gradient-to-br from-violet-500 to-cyan-600'
      )}>
        {isUser ? <User className="w-3.5 h-3.5 text-white" /> : <Bot className="w-3.5 h-3.5 text-white" />}
      </div>

      <div className={cn('flex flex-col gap-1.5 max-w-[75%]', isUser && 'items-end')}>
        {/* Content */}
        <div className={cn(
          'px-4 py-3 rounded-2xl text-sm leading-relaxed',
          isUser
            ? 'bg-cyan-500/10 border border-cyan-500/20 text-foreground rounded-tr-sm'
            : 'bg-surface border border-border text-foreground rounded-tl-sm'
        )}>
          <p className="whitespace-pre-wrap">{msg.content}</p>
        </div>

        {/* Sources */}
        {msg.sources && msg.sources.length > 0 && (
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-[10px] text-muted">Sources:</span>
            {msg.sources.map((s, i) => (
              <div
                key={i}
                className="flex items-center gap-1 text-[11px] px-2 py-0.5 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-400"
              >
                <ExternalLink className="w-2.5 h-2.5" />
                {s.label}
                <span className="opacity-60">{(s.similarity * 100).toFixed(0)}%</span>
              </div>
            ))}
          </div>
        )}

        <span className="text-[10px] text-muted">{formatRelativeTime(msg.timestamp)}</span>
      </div>
    </motion.div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex gap-3">
      <div className="w-7 h-7 rounded-full bg-gradient-to-br from-violet-500 to-cyan-600 flex items-center justify-center shrink-0">
        <Bot className="w-3.5 h-3.5 text-white" />
      </div>
      <div className="px-4 py-3 rounded-2xl rounded-tl-sm bg-surface border border-border flex items-center gap-1.5">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="w-1.5 h-1.5 rounded-full bg-muted"
            animate={{ opacity: [0.3, 1, 0.3] }}
            transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
          />
        ))}
      </div>
    </div>
  );
}

export default function ChatbotPage() {
  const [sessions, setSessions] = useState<ChatSession[]>(mockChatSessions);
  const [activeSessionId, setActiveSessionId] = useState<string>(mockChatSessions[0].id);
  const [messages, setMessages] = useState<ChatMessage[]>(mockInitialMessages);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  const sendMessage = async (content: string) => {
    if (!content.trim() || isTyping) return;
    setInput('');

    const userMsg: ChatMessage = {
      id: `msg_${Date.now()}`,
      session_id: activeSessionId,
      role: 'user',
      content: content.trim(),
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);

    // Simulate streaming delay
    await new Promise((r) => setTimeout(r, 900 + Math.random() * 600));

    const response = getMockResponse(content);
    const aiMsg: ChatMessage = {
      id: `msg_${Date.now() + 1}`,
      session_id: activeSessionId,
      role: 'assistant',
      content: response.content,
      timestamp: new Date().toISOString(),
      sources: response.sources,
    };
    setIsTyping(false);
    setMessages((prev) => [...prev, aiMsg]);
  };

  const newSession = () => {
    const newSess: ChatSession = {
      id: `sess_${Date.now()}`,
      title: 'New conversation',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      message_count: 0,
    };
    setSessions((prev) => [newSess, ...prev]);
    setActiveSessionId(newSess.id);
    setMessages([]);
  };

  return (
    <div className="h-[calc(100vh-56px)] flex overflow-hidden">
      {/* Session sidebar */}
      <div className="w-56 shrink-0 flex flex-col border-r border-border bg-surface overflow-hidden">
        <div className="p-3 border-b border-border">
          <button
            onClick={newSession}
            className="w-full flex items-center justify-center gap-2 py-2 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-medium hover:bg-cyan-500/20 transition-all"
          >
            <Plus className="w-3.5 h-3.5" />
            New Chat
          </button>
        </div>
        <div className="flex-1 overflow-y-auto py-2">
          {sessions.map((sess) => (
            <button
              key={sess.id}
              onClick={() => setActiveSessionId(sess.id)}
              className={cn(
                'w-full flex items-start gap-2.5 px-3 py-2.5 text-left transition-colors',
                activeSessionId === sess.id ? 'bg-surface-2' : 'hover:bg-surface-2'
              )}
            >
              <MessageSquare className="w-3.5 h-3.5 text-muted shrink-0 mt-0.5" />
              <div className="min-w-0">
                <p className={cn(
                  'text-xs truncate',
                  activeSessionId === sess.id ? 'text-foreground font-medium' : 'text-muted'
                )}>
                  {sess.title}
                </p>
                <p className="text-[10px] text-muted mt-0.5">{formatRelativeTime(sess.updated_at)}</p>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Chat area */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center h-full gap-4 text-center">
              <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-500 to-cyan-600 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h2 className="text-base font-bold font-heading text-foreground">Ask Yefai AI</h2>
                <p className="text-xs text-muted mt-1 max-w-xs">
                  Ask about anomalies, wear trends, spare parts, or any production data.
                </p>
              </div>
              <div className="grid grid-cols-2 gap-2 max-w-md w-full">
                {SUGGESTED_PROMPTS.map((p) => (
                  <button
                    key={p}
                    onClick={() => sendMessage(p)}
                    className="px-3 py-2.5 rounded-xl text-xs text-left bg-surface border border-border text-muted hover:text-foreground hover:border-border-strong transition-all"
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          )}

          {messages.map((msg) => (
            <MessageBubble key={msg.id} msg={msg} />
          ))}
          <AnimatePresence>
            {isTyping && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                <TypingIndicator />
              </motion.div>
            )}
          </AnimatePresence>
          <div ref={bottomRef} />
        </div>

        {/* Suggested prompts above input */}
        {messages.length > 0 && (
          <div className="px-6 pb-1 flex gap-2 flex-wrap">
            {SUGGESTED_PROMPTS.slice(0, 2).map((p) => (
              <button
                key={p}
                onClick={() => sendMessage(p)}
                className="text-[11px] px-2.5 py-1 rounded-full bg-surface border border-border text-muted hover:text-foreground hover:border-border-strong transition-all"
              >
                {p}
              </button>
            ))}
          </div>
        )}

        {/* Input */}
        <div className="p-4 border-t border-border">
          <form
            onSubmit={(e) => { e.preventDefault(); sendMessage(input); }}
            className="flex gap-3"
          >
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about wear levels, anomalies, spare parts..."
              disabled={isTyping}
              className="flex-1 px-4 py-2.5 rounded-xl bg-surface border border-border text-foreground text-sm placeholder:text-muted focus:outline-none focus:border-cyan-500/40 focus:ring-1 focus:ring-cyan-500/20 transition-all disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={!input.trim() || isTyping}
              className="px-4 py-2.5 rounded-xl bg-cyan-500 hover:bg-cyan-400 text-background text-sm font-medium transition-all disabled:opacity-40 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
