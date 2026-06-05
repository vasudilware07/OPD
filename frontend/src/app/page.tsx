"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import {
  TrendingUp, FileCheck, FileX, AlertTriangle, Clock, Shield,
  ArrowRight, Activity, DollarSign, PlusCircle, Eye
} from "lucide-react";

interface Stats {
  total_claims: number;
  approved_claims: number;
  rejected_claims: number;
  partial_claims: number;
  pending_claims: number;
  manual_review_claims: number;
  appealed_claims: number;
  total_claimed_amount: number;
  total_approved_amount: number;
  approval_rate: number;
  fraud_flags_count: number;
  recent_claims: any[];
}

function StatCard({ icon: Icon, label, value, sub, color }: any) {
  return (
    <div className="glass-card glass-card-hover p-5">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-text-muted text-xs font-medium uppercase tracking-wider">{label}</p>
          <p className="text-2xl font-bold mt-1" style={{ color }}>{value}</p>
          {sub && <p className="text-text-secondary text-xs mt-1">{sub}</p>}
        </div>
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: `${color}15` }}>
          <Icon size={20} style={{ color }} />
        </div>
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    APPROVED: "status-approved",
    REJECTED: "status-rejected",
    PARTIAL: "status-partial",
    MANUAL_REVIEW: "status-review",
    PENDING: "status-pending",
    APPEALED: "status-review",
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${map[status] || "status-pending"}`}>
      {status.replace("_", " ")}
    </span>
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch("/api/claims/stats")
      .then(setStats)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-plum-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-text-secondary">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-6 py-12">
        <div className="glass-card p-8 text-center">
          <AlertTriangle size={48} className="text-accent-yellow mx-auto mb-4" />
          <h2 className="text-xl font-bold mb-2">Cannot connect to backend</h2>
          <p className="text-text-secondary mb-4">Make sure the FastAPI server is running on port 8000</p>
          <code className="text-sm bg-surface p-3 rounded-lg block text-text-muted">
            cd backend && .\venv\Scripts\python.exe -m uvicorn main:app --reload
          </code>
        </div>
      </div>
    );
  }

  const s = stats!;

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      {/* Hero */}
      <div className="mb-10">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">
              <span className="gradient-text">ClaimGuard</span> Dashboard
            </h1>
            <p className="text-text-secondary mt-1">AI-powered OPD claim adjudication at a glance</p>
          </div>
          <Link href="/claims/new" className="btn-primary flex items-center gap-2">
            <PlusCircle size={18} /> Submit New Claim
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <StatCard icon={Activity} label="Total Claims" value={s.total_claims} color="#a855f7" />
        <StatCard icon={FileCheck} label="Approved" value={s.approved_claims} sub={`${s.approval_rate}% rate`} color="#22c55e" />
        <StatCard icon={FileX} label="Rejected" value={s.rejected_claims} color="#ef4444" />
        <StatCard icon={AlertTriangle} label="Manual Review" value={s.manual_review_claims} sub={`${s.fraud_flags_count} fraud flags`} color="#f59e0b" />
      </div>

      {/* Financial Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <StatCard icon={DollarSign} label="Total Claimed" value={`₹${(s.total_claimed_amount || 0).toLocaleString("en-IN")}`} color="#3b82f6" />
        <StatCard icon={TrendingUp} label="Total Approved" value={`₹${(s.total_approved_amount || 0).toLocaleString("en-IN")}`} color="#22c55e" />
        <StatCard icon={Shield} label="Savings" value={`₹${((s.total_claimed_amount || 0) - (s.total_approved_amount || 0)).toLocaleString("en-IN")}`} sub="Deductions + Rejections" color="#a855f7" />
      </div>

      {/* Recent Claims */}
      <div className="glass-card p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold">Recent Claims</h2>
          <Link href="/claims" className="text-plum-400 text-sm flex items-center gap-1 hover:text-plum-300">
            View All <ArrowRight size={14} />
          </Link>
        </div>
        {s.recent_claims.length === 0 ? (
          <div className="text-center py-12 text-text-muted">
            <Clock size={40} className="mx-auto mb-3 opacity-50" />
            <p>No claims submitted yet</p>
            <Link href="/claims/new" className="text-plum-400 text-sm mt-2 inline-block hover:underline">
              Submit your first claim
            </Link>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-border text-text-muted text-xs uppercase tracking-wider">
                  <th className="text-left py-3 px-3">Claim ID</th>
                  <th className="text-left py-3 px-3">Member</th>
                  <th className="text-left py-3 px-3">Date</th>
                  <th className="text-right py-3 px-3">Amount</th>
                  <th className="text-center py-3 px-3">Status</th>
                  <th className="text-right py-3 px-3">Approved</th>
                  <th className="text-center py-3 px-3">Action</th>
                </tr>
              </thead>
              <tbody>
                {s.recent_claims.map((c: any) => (
                  <tr key={c.claim_id} className="border-b border-surface-border/50 hover:bg-surface-elevated/50 transition-colors">
                    <td className="py-3 px-3 font-mono text-plum-400">{c.claim_id}</td>
                    <td className="py-3 px-3">{c.member_name}</td>
                    <td className="py-3 px-3 text-text-secondary">{c.treatment_date}</td>
                    <td className="py-3 px-3 text-right">₹{c.claim_amount?.toLocaleString("en-IN")}</td>
                    <td className="py-3 px-3 text-center"><StatusBadge status={c.status} /></td>
                    <td className="py-3 px-3 text-right text-accent-green">₹{(c.decision?.approved_amount || 0).toLocaleString("en-IN")}</td>
                    <td className="py-3 px-3 text-center">
                      <Link href={`/claims/${c.claim_id}`} className="text-plum-400 hover:text-plum-300">
                        <Eye size={16} />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
