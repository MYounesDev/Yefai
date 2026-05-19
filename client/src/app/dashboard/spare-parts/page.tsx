'use client';

import { useState, useMemo, useCallback } from 'react';
import { motion, AnimatePresence, type Variants } from 'framer-motion';
import { Package, AlertTriangle, Truck, FileText, Check, X, Search } from 'lucide-react';
import { mockSparePartsCatalog, mockInventorySnapshots, mockPurchaseOrders, mockPartTickets } from '@/services/mock/spareParts';
import { ProgressBar } from '@/components/ui/index';
import { cn, formatCurrency } from '@/lib/utils';

const stagger: { container: Variants; item: Variants } = {
  container: { hidden: {}, show: { transition: { staggerChildren: 0.04 } } },
  item: { hidden: { opacity: 0, y: 10 }, show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 300, damping: 26 } } },
};

type Tab = 'catalog' | 'tickets' | 'orders';

const tabConfig: { id: Tab; label: string; icon: React.ElementType }[] = [
  { id: 'catalog', label: 'Katalog & Stok', icon: Package },
  { id: 'tickets', label: 'Kriz Biletleri', icon: AlertTriangle },
  { id: 'orders', label: 'Satın Alma', icon: Truck },
];

const riskLabels: Record<string, string> = { none: 'Yok', watch: 'İzle', at_risk: 'Risk', crisis: 'Kriz' };
const ticketStatusLabels: Record<string, string> = { planned: 'Planlandı', waiting_part: 'Parça Bekliyor', ordered: 'Sipariş Edildi', stockout: 'Stok Bitti', closed: 'Kapatıldı' };
const poStatusLabels: Record<string, string> = { draft: 'Taslak', ready_for_review: 'İnceleme', approved: 'Onaylandı', rejected: 'Reddedildi' };
const urgencyLabels: Record<string, string> = { normal: 'Normal', rush: 'Acil', critical: 'Kritik' };

export default function SparePartsPage() {
  const [tab, setTab] = useState<Tab>('catalog');
  const [search, setSearch] = useState('');
  const [dismissedOrders, setDismissedOrders] = useState<Record<string, 'approved' | 'rejected'>>({});
  const [flashingOrder, setFlashingOrder] = useState<string | null>(null);

  const handleOrderAction = useCallback((poId: string, action: 'approved' | 'rejected') => {
    setFlashingOrder(poId);
    setTimeout(() => {
      setDismissedOrders((prev) => ({ ...prev, [poId]: action }));
      setFlashingOrder(null);
    }, 600);
  }, []);

  const inventoryMap = useMemo(() => {
    const map: Record<string, typeof mockInventorySnapshots[0]> = {};
    mockInventorySnapshots.forEach((s) => { map[s.part_id] = s; });
    return map;
  }, []);

  const filteredCatalog = useMemo(() => {
    if (!search) return mockSparePartsCatalog;
    return mockSparePartsCatalog.filter((p) =>
      p.name.toLowerCase().includes(search.toLowerCase()) || p.part_number.toLowerCase().includes(search.toLowerCase())
    );
  }, [search]);

  return (
    <div className="p-6 space-y-6">
      {/* Tabs */}
      <div className="flex items-center gap-1 p-1 bg-surface border border-border rounded-xl w-fit">
        {tabConfig.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={cn(
              'flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-medium transition-all',
              tab === t.id
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

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-muted" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Parça adı veya numarası ara..."
          className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-surface border border-border text-sm text-foreground placeholder:text-muted/50 focus:outline-none focus:border-cyan/40 focus:ring-2 focus:ring-cyan/10 transition-all"
        />
      </div>

      {/* CATALOG TAB */}
      {tab === 'catalog' && (
        <motion.div variants={stagger.container} initial="hidden" animate="show" className="space-y-3">
          {/* Header */}
          <div className="grid grid-cols-12 gap-4 px-5 py-3 text-[11px] text-muted font-medium tracking-wide uppercase bg-surface border border-border rounded-t-xl">
            <div className="col-span-3">Parça</div>
            <div className="col-span-2">Sınıf</div>
            <div className="col-span-2">Stok</div>
            <div className="col-span-2">Tedarik Süresi</div>
            <div className="col-span-1">Fiyat</div>
            <div className="col-span-2">Tedarikçi</div>
          </div>
          {filteredCatalog.map((part) => {
            const inv = inventoryMap[part.id];
            const isLow = inv && inv.on_hand <= inv.reorder_point;

            return (
              <motion.div
                key={part.id}
                variants={stagger.item}
                className={cn(
                  'grid grid-cols-12 gap-4 px-5 py-4 bg-surface border rounded-xl items-center transition-all hover:shadow-card',
                  isLow ? 'border-amber/25' : 'border-border'
                )}
              >
                <div className="col-span-3">
                  <p className="text-xs font-semibold text-foreground">{part.name}</p>
                  <p className="text-[10px] font-mono text-muted mt-0.5">{part.part_number}</p>
                </div>
                <div className="col-span-2">
                  <span className={cn(
                    'text-[10px] px-2 py-0.5 rounded-lg font-semibold',
                    part.criticality_class === 'A_vital' ? 'bg-rose/10 text-rose' :
                    part.criticality_class === 'B_essential' ? 'bg-amber/10 text-amber' :
                    'bg-emerald/10 text-emerald'
                  )}>
                    {part.criticality_class.replace('_', ' ')}
                  </span>
                </div>
                <div className="col-span-2">
                  {inv ? (
                    <div className="space-y-1">
                      <div className="flex justify-between text-[10px]">
                        <span className={isLow ? 'text-amber font-semibold' : 'text-muted'}>{inv.on_hand} adet</span>
                        <span className="text-muted">/ {inv.reorder_point}</span>
                      </div>
                      <ProgressBar
                        value={inv.on_hand}
                        max={inv.reorder_point * 2}
                        color={isLow ? 'amber' : 'emerald'}
                        size="xs"
                      />
                    </div>
                  ) : (
                    <span className="text-[10px] text-muted">—</span>
                  )}
                </div>
                <div className="col-span-2">
                  <span className="text-xs text-foreground">{part.lead_time_p50_days}–{part.lead_time_p90_days} gün</span>
                </div>
                <div className="col-span-1">
                  <span className="text-xs font-mono text-foreground">{formatCurrency(part.unit_cost_usd)}</span>
                </div>
                <div className="col-span-2">
                  <span className="text-xs text-muted">{part.supplier_count} tedarikçi</span>
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      )}

      {/* TICKETS TAB */}
      {tab === 'tickets' && (
        <motion.div variants={stagger.container} initial="hidden" animate="show" className="space-y-3">
          {mockPartTickets.map((ticket) => (
            <motion.div
              key={ticket.id}
              variants={stagger.item}
              className={cn(
                'bg-surface border rounded-xl p-5 transition-all',
                ticket.risk_level === 'crisis' ? 'border-rose/25' :
                ticket.risk_level === 'at_risk' ? 'border-amber/25' : 'border-border'
              )}
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-semibold text-foreground">{ticket.part_name}</p>
                    <span className={cn(
                      'text-[10px] px-2 py-0.5 rounded-lg font-semibold',
                      ticket.risk_level === 'crisis' ? 'bg-rose/10 text-rose' :
                      ticket.risk_level === 'at_risk' ? 'bg-amber/10 text-amber' :
                      ticket.risk_level === 'watch' ? 'bg-cyan/10 text-cyan' :
                      'bg-emerald/10 text-emerald'
                    )}>
                      {riskLabels[ticket.risk_level]}
                    </span>
                  </div>
                  <p className="text-[11px] text-muted mt-0.5">{ticket.machine_id} · {ticket.tool_id}</p>
                </div>
                <span className="text-[10px] px-2 py-0.5 rounded-lg bg-surface-2 text-muted font-medium">
                  {ticketStatusLabels[ticket.status]}
                </span>
              </div>

              {/* Risk score breakdown */}
              <div className="grid grid-cols-5 gap-2">
                {[
                  { label: 'Stok Eksikliği', value: ticket.score_breakdown.shortage_probability },
                  { label: 'Tedarik Süre', value: ticket.score_breakdown.lead_time_gap },
                  { label: 'Kritiklik', value: ticket.score_breakdown.criticality },
                  { label: 'Tedarikçi Riski', value: ticket.score_breakdown.supplier_risk },
                  { label: 'Anomali Şiddeti', value: ticket.score_breakdown.anomaly_severity },
                ].map((b) => (
                  <div key={b.label} className="text-center">
                    <p className="text-[9px] text-muted mb-1">{b.label}</p>
                    <ProgressBar value={b.value * 100} max={100} color={b.value > 0.7 ? 'rose' : b.value > 0.4 ? 'amber' : 'emerald'} size="xs" />
                    <p className="text-[10px] font-mono text-muted mt-0.5">{(b.value * 100).toFixed(0)}%</p>
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </motion.div>
      )}

      {/* ORDERS TAB */}
      {tab === 'orders' && (
        <motion.div variants={stagger.container} initial="hidden" animate="show" className="space-y-3">
          <AnimatePresence mode="popLayout">
            {mockPurchaseOrders
              .filter((po) => !dismissedOrders[po.id])
              .map((po) => (
              <motion.div
                key={po.id}
                layout
                variants={stagger.item}
                exit={{
                  opacity: 0,
                  x: dismissedOrders[po.id] === 'rejected' ? -80 : 80,
                  scale: 0.9,
                  transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] },
                }}
                className={cn(
                  'bg-surface border rounded-xl p-5 transition-colors duration-300 overflow-hidden',
                  flashingOrder === po.id ? 'border-cyan/50 shadow-lg shadow-cyan/10' :
                  po.urgency === 'critical' ? 'border-rose/25' :
                  po.urgency === 'rush' ? 'border-amber/25' : 'border-border'
                )}
              >
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <div className="flex items-center gap-2">
                      <FileText className="w-4 h-4 text-muted" />
                      <p className="text-sm font-semibold text-foreground">{po.po_number}</p>
                      <span className={cn(
                        'text-[10px] px-2 py-0.5 rounded-lg font-semibold',
                        po.urgency === 'critical' ? 'bg-rose/10 text-rose' :
                        po.urgency === 'rush' ? 'bg-amber/10 text-amber' :
                        'bg-emerald/10 text-emerald'
                      )}>
                        {urgencyLabels[po.urgency]}
                      </span>
                    </div>
                    <p className="text-[11px] text-muted mt-0.5">{po.part_name} · {po.supplier_name}</p>
                  </div>
                  <span className={cn(
                    'text-[10px] px-2.5 py-1 rounded-lg font-semibold',
                    po.status === 'approved' ? 'bg-emerald/10 text-emerald' :
                    po.status === 'rejected' ? 'bg-rose/10 text-rose' :
                    'bg-cyan/10 text-cyan'
                  )}>
                    {poStatusLabels[po.status]}
                  </span>
                </div>

                <div className="grid grid-cols-4 gap-4 text-xs">
                  <div>
                    <p className="text-[10px] text-muted mb-0.5">Miktar</p>
                    <p className="font-medium text-foreground">{po.quantity} adet</p>
                  </div>
                  <div>
                    <p className="text-[10px] text-muted mb-0.5">Toplam Tutar</p>
                    <p className="font-mono font-medium text-foreground">{formatCurrency(po.total_cost_usd)}</p>
                  </div>
                  <div>
                    <p className="text-[10px] text-muted mb-0.5">Gerekli Tarih</p>
                    <p className="text-foreground">{new Date(po.needed_by).toLocaleDateString('tr-TR')}</p>
                  </div>
                  <div>
                    <p className="text-[10px] text-muted mb-0.5">Tahmini Teslim</p>
                    <p className="text-foreground">{new Date(po.expected_delivery).toLocaleDateString('tr-TR')}</p>
                  </div>
                </div>

                {/* Actions */}
                {po.status === 'ready_for_review' && (
                  <motion.div
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex gap-2 mt-4"
                  >
                    <button
                      onClick={() => handleOrderAction(po.id, 'approved')}
                      disabled={flashingOrder === po.id}
                      className={cn(
                        'flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold transition-all active:scale-95',
                        flashingOrder === po.id
                          ? 'bg-emerald/30 text-emerald scale-105'
                          : 'bg-emerald/10 text-emerald hover:bg-emerald/20'
                      )}
                    >
                      <Check className="w-3.5 h-3.5" /> Onayla
                    </button>
                    <button
                      onClick={() => handleOrderAction(po.id, 'rejected')}
                      disabled={flashingOrder === po.id}
                      className={cn(
                        'flex items-center gap-1.5 px-4 py-2 rounded-lg text-xs font-semibold transition-all active:scale-95',
                        flashingOrder === po.id
                          ? 'bg-rose/30 text-rose scale-105'
                          : 'bg-rose/10 text-rose hover:bg-rose/20'
                      )}
                    >
                      <X className="w-3.5 h-3.5" /> Reddet
                    </button>
                  </motion.div>
                )}
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Empty state when all orders dismissed */}
          {mockPurchaseOrders.filter((po) => !dismissedOrders[po.id]).length === 0 && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex flex-col items-center justify-center py-16 text-center"
            >
              <div className="w-16 h-16 rounded-2xl bg-emerald/10 flex items-center justify-center mb-4">
                <Check className="w-8 h-8 text-emerald" />
              </div>
              <p className="text-sm font-heading font-semibold text-foreground">Tüm talepler işlendi!</p>
              <p className="text-xs text-muted mt-1">Bekleyen satın alma talebi bulunmuyor.</p>
            </motion.div>
          )}
        </motion.div>
      )}
    </div>
  );
}
