'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Eye, EyeOff, LogIn, AlertCircle, Cpu, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import { cn } from '@/lib/utils';

const DEMO_ACCOUNTS = [
  { label: 'Yönetici', email: 'manager@acme.com', password: 'demo123', desc: 'Tam erişim' },
  { label: 'Teknisyen', email: 'tech@acme.com', password: 'demo123', desc: 'Bakım ekibi' },
  { label: 'Satın Alma', email: 'proc@acme.com', password: 'demo123', desc: 'Parça yönetimi' },
  { label: 'Operatör', email: 'op@acme.com', password: 'demo123', desc: 'Makine izleme' },
];

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.08, duration: 0.5, ease: [0.22, 1, 0.36, 1] as const },
  }),
} as const;

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
      setError('Geçersiz kimlik bilgileri. Aşağıdaki demo hesaplarını deneyin.');
    }
  };

  const fillDemo = (acc: typeof DEMO_ACCOUNTS[number]) => {
    setEmail(acc.email);
    setPassword(acc.password);
    setError('');
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4 relative overflow-hidden">
      {/* Background effects */}
      <div className="bg-mesh" />
      <div className="absolute inset-0 bg-dots opacity-30" />

      {/* Back to landing */}
      <Link
        href="/"
        className="absolute top-6 left-6 z-20 flex items-center gap-2 text-xs text-muted hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Ana Sayfa</span>
      </Link>

      <motion.div
        initial="hidden"
        animate="visible"
        className="w-full max-w-md relative z-10"
      >
        {/* Logo */}
        <motion.div variants={fadeUp} custom={0} className="flex flex-col items-center mb-10">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-cyan to-violet flex items-center justify-center mb-4 shadow-xl shadow-cyan/20">
            <Cpu className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold font-heading text-foreground tracking-tight">
            Yefai&apos;ye Hoş Geldiniz
          </h1>
          <p className="text-sm text-muted mt-1.5">Endüstriyel AI Platformu</p>
        </motion.div>

        {/* Card */}
        <motion.div
          variants={fadeUp}
          custom={1}
          className="bg-surface border border-border rounded-2xl p-8 shadow-elevated"
        >
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-xs font-medium text-muted mb-2">E-posta</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 rounded-xl bg-surface-2 border border-border text-foreground text-sm placeholder:text-muted/50 focus:outline-none focus:border-cyan/40 focus:ring-2 focus:ring-cyan/10 transition-all"
                placeholder="isim@sirket.com"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-muted mb-2">Şifre</label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="w-full px-4 py-3 rounded-xl bg-surface-2 border border-border text-foreground text-sm placeholder:text-muted/50 focus:outline-none focus:border-cyan/40 focus:ring-2 focus:ring-cyan/10 transition-all pr-11"
                  placeholder="••••••••"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((p) => !p)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-muted hover:text-foreground transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -6 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-2 px-4 py-3 rounded-xl bg-rose/8 border border-rose/15 text-rose text-xs"
              >
                <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                {error}
              </motion.div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className={cn(
                'w-full flex items-center justify-center gap-2.5 py-3 rounded-xl text-sm font-semibold transition-all active:scale-[0.97]',
                'bg-gradient-to-r from-cyan to-violet text-white shadow-lg shadow-cyan/15 hover:shadow-xl hover:shadow-cyan/25',
                isLoading && 'opacity-60 cursor-not-allowed'
              )}
            >
              {isLoading ? (
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <LogIn className="w-4 h-4" />
              )}
              {isLoading ? 'Giriş yapılıyor...' : 'Giriş Yap'}
            </button>
          </form>

          {/* Demo accounts */}
          <motion.div variants={fadeUp} custom={2} className="mt-8">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex-1 h-px bg-border" />
              <p className="text-[10px] text-muted tracking-widest uppercase">Demo Hesaplar</p>
              <div className="flex-1 h-px bg-border" />
            </div>
            <div className="grid grid-cols-2 gap-2.5">
              {DEMO_ACCOUNTS.map((acc) => (
                <button
                  key={acc.label}
                  onClick={() => fillDemo(acc)}
                  className={cn(
                    'px-3.5 py-3 rounded-xl border text-left transition-all duration-200',
                    email === acc.email
                      ? 'border-cyan/30 bg-cyan/6 text-cyan'
                      : 'border-border bg-surface-2 text-muted hover:border-border-strong hover:text-foreground'
                  )}
                >
                  <div className="text-xs font-semibold">{acc.label}</div>
                  <div className="text-[10px] mt-0.5 opacity-60">{acc.desc}</div>
                </button>
              ))}
            </div>
          </motion.div>
        </motion.div>
      </motion.div>
    </div>
  );
}
