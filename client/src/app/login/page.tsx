'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Eye, EyeOff, LogIn, AlertCircle } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { cn } from '@/lib/utils';

const DEMO_ACCOUNTS = [
  { label: 'Manager', email: 'manager@acme.com', password: 'demo123' },
  { label: 'Technician', email: 'tech@acme.com', password: 'demo123' },
  { label: 'Procurement', email: 'proc@acme.com', password: 'demo123' },
  { label: 'Operator', email: 'op@acme.com', password: 'demo123' },
];

export default function LoginPage() {
  const router = useRouter();
  const { login, isAuthenticated, isLoading } = useAuthStore();
  const [email, setEmail] = useState('manager@acme.com');
  const [password, setPassword] = useState('demo123');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isAuthenticated) router.replace('/dashboard');
  }, [isAuthenticated, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      await login(email, password);
      router.replace('/dashboard');
    } catch {
      setError('Invalid credentials. Try a demo account below.');
    }
  };

  const fillDemo = (acc: typeof DEMO_ACCOUNTS[number]) => {
    setEmail(acc.email);
    setPassword(acc.password);
    setError('');
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4">
      {/* Background grid */}
      <div className="absolute inset-0 bg-[url('/grid.svg')] opacity-[0.03] pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md relative"
      >
        {/* Logo */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-cyan-500 to-violet-600 flex items-center justify-center mb-3 shadow-lg shadow-cyan-500/20">
            <span className="text-white font-bold text-xl font-heading">Y</span>
          </div>
          <h1 className="text-2xl font-bold font-heading text-foreground">Welcome to Yefai</h1>
          <p className="text-sm text-muted mt-1">Industrial AI Platform</p>
        </div>

        {/* Card */}
        <div className="bg-surface border border-border rounded-2xl p-8 shadow-xl">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-muted mb-1.5">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-3 py-2.5 rounded-lg bg-surface-2 border border-border text-foreground text-sm placeholder:text-muted focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 transition-all"
                placeholder="you@company.com"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-muted mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full px-3 py-2.5 rounded-lg bg-surface-2 border border-border text-foreground text-sm placeholder:text-muted focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/20 transition-all pr-10"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((p) => !p)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted hover:text-foreground transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-2 px-3 py-2.5 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs"
              >
                <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                {error}
              </motion.div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className={cn(
                'w-full flex items-center justify-center gap-2 py-2.5 rounded-lg text-sm font-medium transition-all',
                'bg-cyan-500 hover:bg-cyan-400 text-background',
                isLoading && 'opacity-60 cursor-not-allowed'
              )}
            >
              {isLoading ? (
                <span className="w-4 h-4 border-2 border-background/30 border-t-background rounded-full animate-spin" />
              ) : (
                <LogIn className="w-4 h-4" />
              )}
              {isLoading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          {/* Demo accounts */}
          <div className="mt-6">
            <p className="text-xs text-muted text-center mb-3">Demo accounts</p>
            <div className="grid grid-cols-2 gap-2">
              {DEMO_ACCOUNTS.map((acc) => (
                <button
                  key={acc.label}
                  onClick={() => fillDemo(acc)}
                  className={cn(
                    'px-3 py-2 rounded-lg border text-xs font-medium transition-all text-left',
                    email === acc.email
                      ? 'border-cyan-500/40 bg-cyan-500/10 text-cyan-400'
                      : 'border-border bg-surface-2 text-muted hover:border-border-strong hover:text-foreground'
                  )}
                >
                  <div className="font-semibold">{acc.label}</div>
                  <div className="opacity-70 text-[10px] truncate">{acc.email}</div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
