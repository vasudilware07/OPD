"use client";
import { useEffect, useState } from "react";
import { apiFetch, apiPut } from "@/lib/api";
import {
  Settings, Users, Activity, Shield, Save, RefreshCw,
  TrendingUp, AlertTriangle, CheckCircle
} from "lucide-react";

export default function AdminPage() {
  const [stats, setStats] = useState<any>(null);
  const [members, setMembers] = useState<any[]>([]);
  const [policy, setPolicy] = useState<any>(null);
  const [editMode, setEditMode] = useState(false);
  const [saving, setSaving] = useState(false);
  const [policyEdits, setPolicyEdits] = useState({
    annual_limit: 0, per_claim_limit: 0,
  });

  useEffect(() => {
    apiFetch("/api/claims/stats").then(setStats).catch(console.error);
    apiFetch("/api/members?limit=100").then((d) => setMembers(d.members || [])).catch(console.error);
    apiFetch("/api/policy").then((p) => {
      setPolicy(p);
      setPolicyEdits({
        annual_limit: p.coverage_details?.annual_limit || 50000,
        per_claim_limit: p.coverage_details?.per_claim_limit || 5000,
      });
    }).catch(console.error);
  }, []);

  const handleSavePolicy = async () => {
    setSaving(true);
    try {
      await apiPut("/api/policy", {
        coverage_details: {
          ...policy.coverage_details,
          annual_limit: policyEdits.annual_limit,
          per_claim_limit: policyEdits.per_claim_limit,
        },
      });
      const updated = await apiFetch("/api/policy");
      setPolicy(updated);
      setEditMode(false);
    } catch (e) { console.error(e); }
    finally { setSaving(false); }
  };

  const s = stats || {};

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <h1 className="text-2xl font-bold mb-2"><span className="gradient-text">Admin Dashboard</span></h1>
      <p className="text-text-secondary text-sm mb-8">Policy configuration, analytics, and system management</p>

      {/* Analytics Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <MetricCard icon={Activity} label="Total Claims" value={s.total_claims || 0} color="#a855f7" />
        <MetricCard icon={TrendingUp} label="Approval Rate" value={`${s.approval_rate || 0}%`} color="#22c55e" />
        <MetricCard icon={AlertTriangle} label="Fraud Flags" value={s.fraud_flags_count || 0} color="#f59e0b" />
        <MetricCard icon={Users} label="Total Members" value={members.length} color="#3b82f6" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Policy Configuration */}
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-semibold flex items-center gap-2"><Shield size={18} className="text-plum-400" /> Policy Configuration</h2>
            {!editMode ? (
              <button className="btn-secondary text-xs" onClick={() => setEditMode(true)}><Settings size={14} className="inline mr-1" /> Edit</button>
            ) : (
              <div className="flex gap-2">
                <button className="btn-primary text-xs flex items-center gap-1" onClick={handleSavePolicy} disabled={saving}>
                  {saving ? <RefreshCw size={14} className="animate-spin" /> : <Save size={14} />} Save
                </button>
                <button className="btn-secondary text-xs" onClick={() => setEditMode(false)}>Cancel</button>
              </div>
            )}
          </div>
          <div className="space-y-3">
            <EditField label="Annual Limit (₹)" value={policyEdits.annual_limit} disabled={!editMode}
              onChange={(v: string) => setPolicyEdits({ ...policyEdits, annual_limit: Number(v) })} />
            <EditField label="Per-Claim Limit (₹)" value={policyEdits.per_claim_limit} disabled={!editMode}
              onChange={(v: string) => setPolicyEdits({ ...policyEdits, per_claim_limit: Number(v) })} />
            {policy && (
              <>
                <div className="flex justify-between text-sm p-2 bg-surface rounded-lg">
                  <span className="text-text-muted">Policy ID</span><span>{policy.policy_id}</span>
                </div>
                <div className="flex justify-between text-sm p-2 bg-surface rounded-lg">
                  <span className="text-text-muted">Company</span><span>{policy.policy_holder?.company}</span>
                </div>
                <div className="flex justify-between text-sm p-2 bg-surface rounded-lg">
                  <span className="text-text-muted">Employees Covered</span><span>{policy.policy_holder?.employees_covered}</span>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Claims Breakdown */}
        <div className="glass-card p-6">
          <h2 className="font-semibold mb-4 flex items-center gap-2"><Activity size={18} className="text-plum-400" /> Claims Breakdown</h2>
          <div className="space-y-3">
            <BarRow label="Approved" count={s.approved_claims || 0} total={s.total_claims || 1} color="#22c55e" />
            <BarRow label="Rejected" count={s.rejected_claims || 0} total={s.total_claims || 1} color="#ef4444" />
            <BarRow label="Partial" count={s.partial_claims || 0} total={s.total_claims || 1} color="#f59e0b" />
            <BarRow label="Manual Review" count={s.manual_review_claims || 0} total={s.total_claims || 1} color="#3b82f6" />
            <BarRow label="Appealed" count={s.appealed_claims || 0} total={s.total_claims || 1} color="#8b5cf6" />
          </div>
          <div className="mt-4 pt-4 border-t border-surface-border grid grid-cols-2 gap-3">
            <div className="bg-surface p-3 rounded-lg">
              <p className="text-xs text-text-muted">Total Claimed</p>
              <p className="font-bold text-sm">₹{(s.total_claimed_amount || 0).toLocaleString("en-IN")}</p>
            </div>
            <div className="bg-surface p-3 rounded-lg">
              <p className="text-xs text-text-muted">Total Approved</p>
              <p className="font-bold text-sm text-accent-green">₹{(s.total_approved_amount || 0).toLocaleString("en-IN")}</p>
            </div>
          </div>
        </div>

        {/* Members List */}
        <div className="glass-card p-6 lg:col-span-2">
          <h2 className="font-semibold mb-4 flex items-center gap-2"><Users size={18} className="text-plum-400" /> Policy Members</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-surface-border text-text-muted text-xs uppercase tracking-wider">
                  <th className="text-left py-2 px-3">ID</th>
                  <th className="text-left py-2 px-3">Name</th>
                  <th className="text-left py-2 px-3">Department</th>
                  <th className="text-center py-2 px-3">Claims</th>
                  <th className="text-right py-2 px-3">Approved</th>
                  <th className="text-right py-2 px-3">Remaining</th>
                  <th className="text-center py-2 px-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {members.map((m) => (
                  <tr key={m.member_id} className="border-b border-surface-border/50 hover:bg-surface-elevated/50">
                    <td className="py-2 px-3 font-mono text-plum-400 text-xs">{m.member_id}</td>
                    <td className="py-2 px-3">{m.name}</td>
                    <td className="py-2 px-3 text-text-secondary">{m.department || "-"}</td>
                    <td className="py-2 px-3 text-center">{m.claims_summary?.total_claims || 0}</td>
                    <td className="py-2 px-3 text-right text-accent-green">₹{(m.claims_summary?.total_approved_amount || 0).toLocaleString("en-IN")}</td>
                    <td className="py-2 px-3 text-right">₹{(m.claims_summary?.remaining_annual_limit || 50000).toLocaleString("en-IN")}</td>
                    <td className="py-2 px-3 text-center">
                      <span className="status-approved text-xs px-2 py-0.5 rounded-full">{m.policy_status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

function MetricCard({ icon: Icon, label, value, color }: any) {
  return (
    <div className="glass-card p-4">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: `${color}15` }}>
          <Icon size={18} style={{ color }} />
        </div>
        <div>
          <p className="text-xs text-text-muted">{label}</p>
          <p className="text-lg font-bold" style={{ color }}>{value}</p>
        </div>
      </div>
    </div>
  );
}

function EditField({ label, value, disabled, onChange }: any) {
  return (
    <div className="flex items-center justify-between bg-surface p-3 rounded-lg">
      <label className="text-sm text-text-muted">{label}</label>
      <input type="number" value={value} disabled={disabled} onChange={(e) => onChange(e.target.value)}
        className={`w-32 text-right bg-transparent font-bold text-sm ${disabled ? "text-text-primary" : "input-field !w-32 !p-1 text-right"}`} />
    </div>
  );
}

function BarRow({ label, count, total, color }: any) {
  const pct = total > 0 ? (count / total) * 100 : 0;
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span>{label}</span>
        <span className="font-bold">{count}</span>
      </div>
      <div className="w-full bg-surface rounded-full h-2">
        <div className="h-2 rounded-full transition-all" style={{ width: `${pct}%`, background: color }} />
      </div>
    </div>
  );
}
