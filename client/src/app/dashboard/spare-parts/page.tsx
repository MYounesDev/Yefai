'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Package, AlertTriangle, CheckCircle2, Clock, X, ChevronRight } from 'lucide-react';
import { mockPartTickets, mockPurchaseOrders, mockInventorySnapshots, mockSparePartsCatalog } from '@/services/mock/spareParts';
import { RiskBadge } from '@/components/ui/badge';
import { cn, formatRelativeTime, formatCurrency } from '@/lib/utils';
import type { RiskLevel, POStatus, POUrgency } from '@/types';

const RISK_ORDER: RiskLevel[] = ['crisis', 'at_risk', 'watch', 'none'];

const URGENCY_STYLES: Record<POUrgency, string> = {
  critical: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
  rush: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  normal: 'bg-surface-2 text-muted border-border',
};

const PO_STATUS_STYLES: Record<POStatus, string> = {
  ready_for_review: 'bg-amber-500/10 text-amber-400',
  draft: 'bg-surface-2 text-muted',
  approved: 'bg-emerald-500/10 text-emerald-400',
  rejected: 'bg-rose-500/10 text-rose-400',
};

function POReviewModal({ poId, onClose }: { poId: string; onClose: () => void }) {
  const po = mockPurchaseOrders.find((p) => p.id === poId);
  if (!po) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="w-full max-w-lg bg-surface border border-border rounded-2xl p-6 shadow-2xl"
      >
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-base font-bold font-heading text-foreground">{po.po_number}</h2>
            <p className="text-xs text-muted mt-0.5">{po.part_name}</p>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg text-muted hover:text-foreground hover:bg-surface-2 transition-colors">
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-surface-2 rounded-xl p-3">
              <p className="text-[11px] text-muted mb-0.5">Primary Supplier</p>
              <p className="text-sm font-medium text-foreground">{po.supplier_name}</p>
              <p className="text-[11px] text-muted mt-1">Lead time: {new Date(po.expected_delivery).toLocaleDateString()}</p>
              <p className="text-[11px] font-mono text-foreground">{formatCurrency(po.total_cost_usd)}</p>
            </div>
            {po.alternative_supplier_name && (
              <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-xl p-3">
                <p className="text-[11px] text-emerald-400 mb-0.5">Alternative (faster)</p>
                <p className="text-sm font-medium text-foreground">{po.alternative_supplier_name}</p>
                <p className="text-[11px] text-muted mt-1">+{po.alternative_lead_time_days}d faster</p>
                <p className="text-[11px] font-mono text-foreground">
                  {po.alternative_cost_delta_pct && po.alternative_cost_delta_pct > 0 ? '+' : ''}{po.alternative_cost_delta_pct}% cost
                </p>
              </div>
            )}
          </div>

          <div className="bg-surface-2 rounded-xl p-3 grid grid-cols-3 gap-3 text-xs">
            <div>
              <p className="text-muted">Quantity</p>
              <p className="text-foreground font-mono">{po.quantity} units</p>
            </div>
            <div>
              <p className="text-muted">Total</p>
              <p className="text-foreground font-mono">{formatCurrency(po.total_cost_usd)}</p>
            </div>
            <div>
              <p className="text-muted">Needed by</p>
              <p className="text-foreground">{new Date(po.needed_by).toLocaleDateString()}</p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 mt-5">
          <button
            onClick={onClose}
            className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-sm font-medium hover:bg-rose-500/20 transition-all"
          >
            <X className="w-4 h-4" />
            Reject
          </button>
          <button
            onClick={onClose}
            className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-sm font-medium hover:bg-cyan-500/20 transition-all"
          >
            <CheckCircle2 className="w-4 h-4" />
            Approve PO
          </button>
        </div>
      </motion.div>
    </div>
  );
}

export default function SparePartsPage() {
  const [reviewPO, setReviewPO] = useState<string | null>(null);

  const sortedTickets = [...mockPartTickets].sort(
    (a, b) => RISK_ORDER.indexOf(a.risk_level) - RISK_ORDER.indexOf(b.risk_level)
  );

  const pendingPOs = mockPurchaseOrders.filter((po) => po.status === 'ready_for_review');
  const crisisCount = mockPartTickets.filter((t) => t.risk_level === 'crisis').length;
  const atRiskCount = mockPartTickets.filter((t) => t.risk_level === 'at_risk').length;

  return (
    <div className="p-6 space-y-6">
      {/* Summary strip */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-rose-500/10 border border-rose-500/20">
          <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />
          <span className="text-xs text-rose-400 font-medium">{crisisCount} Crisis</span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20">
          <Clock className="w-3.5 h-3.5 text-amber-400" />
          <span className="text-xs text-amber-400 font-medium">{atRiskCount} At Risk</span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20">
          <Package className="w-3.5 h-3.5 text-amber-400" />
          <span className="text-xs text-amber-400 font-medium">{pendingPOs.length} POs Need Review</span>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Ticket board */}
        <div className="xl:col-span-2 space-y-3">
          <h2 className="text-sm font-semibold text-foreground font-heading">Part Tickets — Crisis Board</h2>
          <div className="space-y-2">
            {sortedTickets.map((ticket, i) => {
              const inv = mockInventorySnapshots.find((s) => s.part_id === ticket.part_id);
              return (
                <motion.div
                  key={ticket.id}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.03 }}
                  className={cn(
                    'bg-surface border rounded-xl p-4',
                    ticket.risk_level === 'crisis' ? 'border-rose-500/30' :
                    ticket.risk_level === 'at_risk' ? 'border-amber-500/30' :
                    ticket.risk_level === 'watch' ? 'border-cyan-500/20' : 'border-border'
                  )}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className="text-sm font-medium text-foreground">{ticket.part_name}</span>
                        <RiskBadge level={ticket.risk_level} />
                        <span className="text-xs text-muted">{ticket.machine_id}</span>
                      </div>
                      <p className="text-[11px] text-muted mt-1">
                        Stock: <span className={cn('font-mono font-medium', (inv?.on_hand ?? 0) === 0 ? 'text-rose-400' : 'text-amber-400')}>{inv?.on_hand ?? 0}</span>
                        {' '}/ ROP: <span className="font-mono">{inv?.reorder_point ?? 0}</span>
                        {inv?.on_order ? <span className="ml-2 text-emerald-400">+{inv.on_order} on order</span> : null}
                      </p>
                    </div>

                    <div className="text-right shrink-0 space-y-1">
                      <div className="text-[11px] text-rose-400">
                        Need by: {new Date(ticket.needed_by).toLocaleDateString()}
                      </div>
                      {ticket.auto_po_id && (
                        <button
                          onClick={() => setReviewPO(ticket.auto_po_id!)}
                          className="flex items-center gap-1 text-[11px] px-2.5 py-1 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/20 transition-all"
                        >
                          Review PO <ChevronRight className="w-3 h-3" />
                        </button>
                      )}
                    </div>
                  </div>

                  {/* Score breakdown */}
                  <div className="mt-3 flex items-center gap-2 flex-wrap">
                    {Object.entries(ticket.score_breakdown).map(([k, v]) => (
                      <div key={k} className="flex items-center gap-1 text-[10px]">
                        <span className="text-muted capitalize">{k.replace('_', ' ')}:</span>
                        <span className="font-mono text-foreground">{(v as number).toFixed(0)}</span>
                      </div>
                    ))}
                    <span className="ml-auto text-[11px] font-bold text-foreground">Score: {ticket.stockout_risk_score}</span>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </div>

        {/* PO Review queue */}
        <div className="space-y-3">
          <h2 className="text-sm font-semibold text-foreground font-heading">Purchase Orders</h2>
          <div className="space-y-2">
            {mockPurchaseOrders.map((po, i) => (
              <motion.div
                key={po.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
                className="bg-surface border border-border rounded-xl p-4 space-y-3"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono text-muted">{po.po_number}</span>
                      <span className={cn('text-[10px] px-2 py-0.5 rounded-full font-medium border', URGENCY_STYLES[po.urgency])}>
                        {po.urgency}
                      </span>
                    </div>
                    <p className="text-sm font-medium text-foreground mt-0.5">{po.part_name}</p>
                    <p className="text-[11px] text-muted">{po.supplier_name}</p>
                  </div>
                  <span className={cn('text-[11px] px-2 py-0.5 rounded-full font-medium shrink-0', PO_STATUS_STYLES[po.status])}>
                    {po.status.replace('_', ' ')}
                  </span>
                </div>

                <div className="flex items-center justify-between text-xs">
                  <span className="font-mono text-foreground">{formatCurrency(po.total_cost_usd)}</span>
                  <span className="text-muted">{po.quantity} units</span>
                </div>

                {po.status === 'ready_for_review' && (
                  <button
                    onClick={() => setReviewPO(po.id)}
                    className="w-full py-1.5 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-medium hover:bg-cyan-500/20 transition-all"
                  >
                    Review & Approve
                  </button>
                )}
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {reviewPO && <POReviewModal poId={reviewPO} onClose={() => setReviewPO(null)} />}
    </div>
  );
}
