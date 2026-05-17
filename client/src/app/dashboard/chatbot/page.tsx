'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Loader2, MessageSquare, Plus, Sparkles } from 'lucide-react';
import { sendChatMessage, getChatSessions } from '@/services/api';
import { cn } from '@/lib/utils';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
  images?: { url: string; metadata: { set: string; wear_level: number; machine_id: string; anomaly_score: number } }[];
  sources?: { label: string; similarity: number }[];
}

const suggestedQueries = [
  'M-03 makinesinin aşınma durumu nedir?',
  'Son 24 saatteki kritik anomalileri listele',
  'Karbür uçların stok durumunu kontrol et',
  'En yüksek aşınma hızına sahip makine hangisi?',
];

export default function ChatbotPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Merhaba! Ben Yefai AI Asistanı. Fabrika verileriniz, anomaliler, tahminler ve yedek parçalar hakkında sorularınızı yanıtlayabilirim. Size nasıl yardımcı olabilirim?',
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async (text?: string) => {
    const messageText = text || input.trim();
    if (!messageText || isLoading) return;

    const userMessage: Message = {
      id: `user_${Date.now()}`,
      role: 'user',
      content: messageText,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage('session_default', messageText);
      const assistantMessage: Message = {
        id: response.id || `ai_${Date.now()}`,
        role: 'assistant',
        content: response.content || 'Yanıt oluşturulamadı.',
        timestamp: response.timestamp || new Date().toISOString(),
        images: response.images,
        sources: response.sources,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch {
      setMessages((prev) => [...prev, {
        id: `err_${Date.now()}`,
        role: 'assistant',
        content: 'Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.',
        timestamp: new Date().toISOString(),
      }]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      {/* Chat Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-border bg-surface/60 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan to-violet flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <h2 className="text-sm font-heading font-bold text-foreground">Yefai AI Asistan</h2>
            <p className="text-[10px] text-muted">RAG destekli · Gerçek zamanlı veri erişimi</p>
          </div>
        </div>
        <button className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-surface-2 border border-border text-xs text-muted hover:text-foreground hover:border-border-strong transition-all">
          <Plus className="w-3.5 h-3.5" />
          Yeni Sohbet
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6">
        <AnimatePresence>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className={cn('flex gap-3', msg.role === 'user' ? 'justify-end' : 'justify-start')}
            >
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-cyan to-violet flex items-center justify-center shrink-0 mt-0.5">
                  <Bot className="w-4 h-4 text-white" />
                </div>
              )}

              <div className={cn(
                'max-w-[70%] rounded-2xl px-5 py-3.5',
                msg.role === 'user'
                  ? 'bg-cyan/10 border border-cyan/15 text-foreground'
                  : 'bg-surface border border-border text-foreground'
              )}>
                <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.content}</p>

                {/* Sources */}
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-border/50 space-y-1.5">
                    <p className="text-[10px] text-muted font-medium tracking-wide uppercase">Kaynaklar</p>
                    {msg.sources.map((src, i) => (
                      <div key={i} className="flex items-center gap-2 text-[11px]">
                        <span className="text-cyan font-medium">{src.label}</span>
                        <span className="text-muted font-mono">({(src.similarity * 100).toFixed(0)}%)</span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Images */}
                {msg.images && msg.images.length > 0 && (
                  <div className="mt-3 grid grid-cols-2 gap-2">
                    {msg.images.map((img, i) => (
                      <div key={i} className="rounded-lg bg-surface-2 border border-border p-2">
                        <div className="aspect-square rounded bg-surface-3 flex items-center justify-center text-[10px] text-muted">
                          {img.metadata.machine_id}
                        </div>
                        <p className="text-[9px] text-muted mt-1 font-mono">
                          Aşınma: {img.metadata.wear_level}µm · Skor: {img.metadata.anomaly_score}
                        </p>
                      </div>
                    ))}
                  </div>
                )}

                <p className="text-[10px] text-muted/60 mt-2">
                  {new Date(msg.timestamp).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}
                </p>
              </div>

              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-xl bg-surface-2 border border-border flex items-center justify-center shrink-0 mt-0.5">
                  <User className="w-4 h-4 text-muted" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Loading indicator */}
        {isLoading && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex gap-3"
          >
            <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-cyan to-violet flex items-center justify-center shrink-0">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="bg-surface border border-border rounded-2xl px-5 py-3.5">
              <div className="flex items-center gap-2 text-sm text-muted">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Düşünüyorum...</span>
              </div>
            </div>
          </motion.div>
        )}

        {/* Suggested queries (show when only welcome message) */}
        {messages.length === 1 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="space-y-3"
          >
            <p className="text-xs text-muted">Önerilen sorular:</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {suggestedQueries.map((q) => (
                <button
                  key={q}
                  onClick={() => handleSend(q)}
                  className="text-left px-4 py-3 rounded-xl bg-surface border border-border text-xs text-foreground hover:border-cyan/25 hover:bg-cyan/4 transition-all group"
                >
                  <MessageSquare className="w-3.5 h-3.5 text-muted group-hover:text-cyan mb-1.5 transition-colors" />
                  {q}
                </button>
              ))}
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="px-6 py-4 border-t border-border bg-surface/80 backdrop-blur-xl">
        <form
          onSubmit={(e) => { e.preventDefault(); handleSend(); }}
          className="flex gap-3"
        >
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Bir soru sorun..."
            disabled={isLoading}
            className="flex-1 px-4 py-3 rounded-xl bg-surface-2 border border-border text-sm text-foreground placeholder:text-muted/50 focus:outline-none focus:border-cyan/40 focus:ring-2 focus:ring-cyan/10 transition-all disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={cn(
              'px-5 py-3 rounded-xl text-sm font-semibold transition-all active:scale-95',
              input.trim() && !isLoading
                ? 'bg-gradient-to-r from-cyan to-violet text-white shadow-lg shadow-cyan/15'
                : 'bg-surface-2 text-muted cursor-not-allowed'
            )}
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
