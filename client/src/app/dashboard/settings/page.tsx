'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Bell, Sliders, Globe, Save } from 'lucide-react';
import { cn } from '@/lib/utils';

function Toggle({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      onClick={() => onChange(!checked)}
      className={cn(
        'relative w-10 h-5 rounded-full transition-colors shrink-0',
        checked ? 'bg-cyan-500' : 'bg-surface-3'
      )}
      role="switch"
      aria-checked={checked}
    >
      <span className={cn(
        'absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform',
        checked ? 'translate-x-5' : 'translate-x-0'
      )} />
    </button>
  );
}

function Section({ title, icon: Icon, children }: { title: string; icon: React.ElementType; children: React.ReactNode }) {
  return (
    <div className="bg-surface border border-border rounded-xl p-5 space-y-4">
      <div className="flex items-center gap-2 pb-1 border-b border-border">
        <Icon className="w-4 h-4 text-cyan-400" />
        <h2 className="text-sm font-semibold font-heading text-foreground">{title}</h2>
      </div>
      {children}
    </div>
  );
}

export default function SettingsPage() {
  const [notifications, setNotifications] = useState({
    telegram: true,
    email: true,
    sms: false,
    anomaly_alert: true,
    critical_warning: true,
    crisis_alert: true,
    report: false,
    po_notification: true,
  });

  const [thresholds, setThresholds] = useState({
    criticalWearUm: 200,
    crisisScoreMin: 60,
    refreshIntervalSec: 30,
    criticalHoursAlert: 24,
  });

  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="p-6 space-y-5 max-w-3xl">
      {/* Notification channels */}
      <Section title="Notification Channels" icon={Bell}>
        <div className="space-y-3">
          {[
            { key: 'telegram', label: 'Telegram', desc: 'Bot-based push notifications' },
            { key: 'email', label: 'Email', desc: 'SMTP delivery to team addresses' },
            { key: 'sms', label: 'SMS', desc: 'Text message alerts for critical events' },
          ].map((ch) => (
            <div key={ch.key} className="flex items-center justify-between py-1">
              <div>
                <p className="text-sm text-foreground">{ch.label}</p>
                <p className="text-xs text-muted">{ch.desc}</p>
              </div>
              <Toggle
                checked={notifications[ch.key as keyof typeof notifications] as boolean}
                onChange={(v) => setNotifications((p) => ({ ...p, [ch.key]: v }))}
              />
            </div>
          ))}
        </div>

        <div className="pt-3 border-t border-border space-y-3">
          <p className="text-xs font-medium text-muted">Alert types</p>
          {[
            { key: 'anomaly_alert', label: 'Anomaly Alerts' },
            { key: 'critical_warning', label: 'Critical Warnings' },
            { key: 'crisis_alert', label: 'Crisis Alerts' },
            { key: 'po_notification', label: 'PO Notifications' },
            { key: 'report', label: 'Weekly Reports' },
          ].map((t) => (
            <div key={t.key} className="flex items-center justify-between py-0.5">
              <p className="text-sm text-foreground">{t.label}</p>
              <Toggle
                checked={notifications[t.key as keyof typeof notifications] as boolean}
                onChange={(v) => setNotifications((p) => ({ ...p, [t.key]: v }))}
              />
            </div>
          ))}
        </div>
      </Section>

      {/* Alert thresholds */}
      <Section title="Alert Thresholds" icon={Sliders}>
        <div className="grid grid-cols-2 gap-4">
          {[
            { key: 'criticalWearUm', label: 'Critical Wear (µm)', min: 100, max: 500, step: 10 },
            { key: 'crisisScoreMin', label: 'Crisis Score Threshold', min: 0, max: 100, step: 5 },
            { key: 'refreshIntervalSec', label: 'Refresh Interval (s)', min: 10, max: 300, step: 10 },
            { key: 'criticalHoursAlert', label: 'Critical Hours Alert', min: 6, max: 96, step: 6 },
          ].map((field) => (
            <div key={field.key} className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs text-muted">{field.label}</label>
                <span className="text-xs font-mono text-foreground">{thresholds[field.key as keyof typeof thresholds]}</span>
              </div>
              <input
                type="range"
                min={field.min}
                max={field.max}
                step={field.step}
                value={thresholds[field.key as keyof typeof thresholds]}
                onChange={(e) => setThresholds((p) => ({ ...p, [field.key]: Number(e.target.value) }))}
                className="w-full accent-cyan-500"
              />
            </div>
          ))}
        </div>
      </Section>

      {/* Organization info */}
      <Section title="Organization" icon={Globe}>
        <div className="space-y-3">
          <div>
            <label className="text-xs text-muted mb-1 block">Organization Name</label>
            <input
              defaultValue="Yılmaz Makina A.Ş."
              className="w-full px-3 py-2 text-sm bg-surface-2 border border-border rounded-lg text-foreground focus:outline-none focus:border-cyan-500/40 focus:ring-1 focus:ring-cyan-500/20 transition-all"
            />
          </div>
          <div>
            <label className="text-xs text-muted mb-1 block">Timezone</label>
            <select className="w-full px-3 py-2 text-sm bg-surface-2 border border-border rounded-lg text-foreground focus:outline-none focus:border-cyan-500/40 transition-all">
              <option>Europe/Istanbul (UTC+3)</option>
              <option>UTC</option>
              <option>America/New_York (UTC-5)</option>
            </select>
          </div>
        </div>
      </Section>

      {/* Save */}
      <motion.button
        onClick={handleSave}
        whileTap={{ scale: 0.97 }}
        className={cn(
          'flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all',
          saved ? 'bg-emerald-500 text-white' : 'bg-cyan-500 hover:bg-cyan-400 text-background'
        )}
      >
        <Save className="w-4 h-4" />
        {saved ? 'Saved!' : 'Save Settings'}
      </motion.button>
    </div>
  );
}
