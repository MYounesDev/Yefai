'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Settings, Bell, Shield, Key, Globe, Palette, Save } from 'lucide-react';
import { cn } from '@/lib/utils';

type Tab = 'general' | 'notifications' | 'security' | 'api';

const tabs: { id: Tab; label: string; icon: React.ElementType }[] = [
  { id: 'general', label: 'Genel', icon: Settings },
  { id: 'notifications', label: 'Bildirimler', icon: Bell },
  { id: 'security', label: 'Güvenlik', icon: Shield },
  { id: 'api', label: 'API Anahtarları', icon: Key },
];

function Toggle({ enabled, onChange, label, desc }: { enabled: boolean; onChange: (v: boolean) => void; label: string; desc?: string }) {
  return (
    <div className="flex items-center justify-between py-4 border-b border-border/50 last:border-0">
      <div>
        <p className="text-sm text-foreground font-medium">{label}</p>
        {desc && <p className="text-[11px] text-muted mt-0.5">{desc}</p>}
      </div>
      <button
        onClick={() => onChange(!enabled)}
        className={cn(
          'relative w-11 h-6 rounded-full transition-colors duration-200',
          enabled ? 'bg-cyan' : 'bg-surface-3'
        )}
      >
        <motion.div
          animate={{ x: enabled ? 20 : 2 }}
          transition={{ type: 'spring', stiffness: 500, damping: 30 }}
          className="absolute top-1 w-4 h-4 rounded-full bg-white shadow-sm"
        />
      </button>
    </div>
  );
}

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<Tab>('general');
  const [telegram, setTelegram] = useState(true);
  const [email, setEmail] = useState(true);
  const [sms, setSms] = useState(false);
  const [criticalOnly, setCriticalOnly] = useState(false);
  const [twoFactor, setTwoFactor] = useState(false);
  const [autoLogout, setAutoLogout] = useState(true);
  const [webhookUrl, setWebhookUrl] = useState('https://hooks.example.com/yefai');
  const [telegramBotToken, setTelegramBotToken] = useState('');
  const [criticalHours, setCriticalHours] = useState('48');
  const [refreshInterval, setRefreshInterval] = useState('30');

  return (
    <div className="p-6">
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Tabs */}
        <div className="flex items-center gap-1 p-1 bg-surface border border-border rounded-xl w-fit">
          {tabs.map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              className={cn(
                'flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-medium transition-all',
                activeTab === t.id
                  ? 'bg-cyan/10 text-cyan border border-cyan/20'
                  : 'text-muted hover:text-foreground'
              )}
            >
              {/* @ts-expect-error - icon is ElementType and accepts className */}
              <t.icon className="w-3.5 h-3.5" />
              {t.label}
            </button>
          ))}
        </div>

        {/* GENERAL */}
        {activeTab === 'general' && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            <div className="bg-surface border border-border rounded-xl p-6">
              <h3 className="text-sm font-heading font-semibold text-foreground mb-4 flex items-center gap-2">
                <Globe className="w-4 h-4 text-cyan" />
                Platform Ayarları
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-muted mb-2">Kritik Eşik (saat)</label>
                  <input
                    type="number"
                    value={criticalHours}
                    onChange={(e) => setCriticalHours(e.target.value)}
                    className="w-full max-w-xs px-4 py-2.5 rounded-xl bg-surface-2 border border-border text-sm text-foreground focus:outline-none focus:border-cyan/40 focus:ring-2 focus:ring-cyan/10 transition-all"
                  />
                  <p className="text-[10px] text-muted mt-1">Makinelerin kritik olarak işaretleneceği saat eşiği</p>
                </div>
                <div>
                  <label className="block text-xs font-medium text-muted mb-2">Yenileme Aralığı (saniye)</label>
                  <input
                    type="number"
                    value={refreshInterval}
                    onChange={(e) => setRefreshInterval(e.target.value)}
                    className="w-full max-w-xs px-4 py-2.5 rounded-xl bg-surface-2 border border-border text-sm text-foreground focus:outline-none focus:border-cyan/40 focus:ring-2 focus:ring-cyan/10 transition-all"
                  />
                  <p className="text-[10px] text-muted mt-1">Dashboard verilerinin otomatik yenilenme süresi</p>
                </div>
              </div>
            </div>

            <div className="bg-surface border border-border rounded-xl p-6">
              <h3 className="text-sm font-heading font-semibold text-foreground mb-4 flex items-center gap-2">
                <Palette className="w-4 h-4 text-violet" />
                Görünüm
              </h3>
              <p className="text-xs text-muted">
                Tema değiştirmek için üst çubuktaki güneş/ay simgesini kullanabilirsiniz.
              </p>
            </div>
          </motion.div>
        )}

        {/* NOTIFICATIONS */}
        {activeTab === 'notifications' && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            <div className="bg-surface border border-border rounded-xl p-6">
              <h3 className="text-sm font-heading font-semibold text-foreground mb-1">Bildirim Kanalları</h3>
              <p className="text-[11px] text-muted mb-4">Uyarıların gönderileceği kanalları seçin</p>
              <Toggle enabled={telegram} onChange={setTelegram} label="Telegram" desc="Kritik ve uyarı bildirimleri Telegram'a gönderilir" />
              <Toggle enabled={email} onChange={setEmail} label="E-posta" desc="Tüm bildirimler e-posta ile gönderilir" />
              <Toggle enabled={sms} onChange={setSms} label="SMS" desc="Yalnızca kritik uyarılar SMS ile gönderilir" />
              <Toggle enabled={criticalOnly} onChange={setCriticalOnly} label="Sadece Kritik Uyarılar" desc="Yalnızca kritik şiddetteki anomalilerde bildirim gönder" />
            </div>

            <div className="bg-surface border border-border rounded-xl p-6">
              <h3 className="text-sm font-heading font-semibold text-foreground mb-4">Webhook Ayarları</h3>
              <div>
                <label className="block text-xs font-medium text-muted mb-2">Webhook URL</label>
                <input
                  type="url"
                  value={webhookUrl}
                  onChange={(e) => setWebhookUrl(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-surface-2 border border-border text-sm text-foreground font-mono focus:outline-none focus:border-cyan/40 focus:ring-2 focus:ring-cyan/10 transition-all"
                  placeholder="https://hooks.example.com/..."
                />
              </div>
            </div>
          </motion.div>
        )}

        {/* SECURITY */}
        {activeTab === 'security' && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
            <div className="bg-surface border border-border rounded-xl p-6">
              <h3 className="text-sm font-heading font-semibold text-foreground mb-1">Güvenlik Ayarları</h3>
              <p className="text-[11px] text-muted mb-4">Hesap güvenliği yapılandırması</p>
              <Toggle enabled={twoFactor} onChange={setTwoFactor} label="İki Faktörlü Doğrulama" desc="Giriş yaparken ekstra güvenlik katmanı" />
              <Toggle enabled={autoLogout} onChange={setAutoLogout} label="Otomatik Çıkış" desc="30 dakika hareketsizlik sonrası otomatik çıkış" />
            </div>
          </motion.div>
        )}

        {/* API */}
        {activeTab === 'api' && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}>
            <div className="bg-surface border border-border rounded-xl p-6">
              <h3 className="text-sm font-heading font-semibold text-foreground mb-1">API Anahtarları</h3>
              <p className="text-[11px] text-muted mb-4">Harici entegrasyonlar için API anahtarlarınız</p>
              <div className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-muted mb-2">Telegram Bot Token</label>
                  <input
                    type="password"
                    value={telegramBotToken}
                    onChange={(e) => setTelegramBotToken(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl bg-surface-2 border border-border text-sm text-foreground font-mono focus:outline-none focus:border-cyan/40 focus:ring-2 focus:ring-cyan/10 transition-all"
                    placeholder="bot123456:ABC-DEF..."
                  />
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Save */}
        <div className="flex justify-end">
          <button className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan to-violet text-white text-sm font-semibold shadow-lg shadow-cyan/15 hover:shadow-xl hover:shadow-cyan/25 transition-all active:scale-95">
            <Save className="w-4 h-4" />
            Değişiklikleri Kaydet
          </button>
        </div>
      </div>
    </div>
  );
}
