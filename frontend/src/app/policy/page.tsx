"use client";
import { useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";
import { Shield, ChevronDown, ChevronRight, AlertTriangle, DollarSign, Clock, XCircle } from "lucide-react";

export default function PolicyPage() {
  const [policy, setPolicy] = useState<any>(null);
  const [expanded, setExpanded] = useState<string[]>(["coverage"]);

  useEffect(() => {
    apiFetch("/api/policy").then(setPolicy).catch(console.error);
  }, []);

  const toggle = (key: string) =>
    setExpanded((prev) => prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]);

  if (!policy) return <div className="min-h-screen flex items-center justify-center text-text-muted">Loading policy...</div>;

  const cov = policy.coverage_details || {};

  const sections = [
    {
      key: "coverage",
      title: "Coverage Details",
      icon: DollarSign,
      content: (
        <div className="space-y-3">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            <Stat label="Annual Limit" value={`₹${cov.annual_limit?.toLocaleString("en-IN")}`} />
            <Stat label="Per-Claim Limit" value={`₹${cov.per_claim_limit?.toLocaleString("en-IN")}`} />
            <Stat label="Family Floater" value={`₹${cov.family_floater_limit?.toLocaleString("en-IN")}`} />
          </div>
          <h4 className="text-sm font-semibold mt-4 mb-2 text-plum-300">Sub-Limits by Category</h4>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
            {Object.entries(cov).filter(([_, v]) => typeof v === "object" && (v as any)?.sub_limit).map(([key, val]: any) => (
              <div key={key} className="bg-surface p-3 rounded-lg">
                <p className="text-xs text-text-muted capitalize">{key.replace("_", " ")}</p>
                <p className="font-bold">₹{val.sub_limit?.toLocaleString("en-IN")}</p>
                {val.copay_percentage && <p className="text-xs text-text-muted">{val.copay_percentage}% co-pay</p>}
              </div>
            ))}
          </div>
        </div>
      ),
    },
    {
      key: "exclusions",
      title: "Exclusions",
      icon: XCircle,
      content: (
        <div className="space-y-2">
          {policy.exclusions?.map((e: string, i: number) => (
            <div key={i} className="flex items-center gap-2 text-sm p-2 rounded-lg bg-surface">
              <span className="text-accent-red">✗</span> {e}
            </div>
          ))}
        </div>
      ),
    },
    {
      key: "waiting",
      title: "Waiting Periods",
      icon: Clock,
      content: (
        <div className="space-y-2">
          <Stat label="Initial Waiting" value={`${policy.waiting_periods?.initial_waiting} days`} />
          <Stat label="Pre-existing Diseases" value={`${policy.waiting_periods?.pre_existing_diseases} days`} />
          <Stat label="Maternity" value={`${policy.waiting_periods?.maternity} days`} />
          <h4 className="text-sm font-semibold mt-4 mb-2 text-plum-300">Specific Ailments</h4>
          {Object.entries(policy.waiting_periods?.specific_ailments || {}).map(([k, v]: any) => (
            <div key={k} className="flex justify-between bg-surface p-2 rounded text-sm">
              <span className="capitalize">{k.replace("_", " ")}</span>
              <span className="font-bold">{v} days</span>
            </div>
          ))}
        </div>
      ),
    },
    {
      key: "requirements",
      title: "Claim Requirements",
      icon: AlertTriangle,
      content: (
        <div className="space-y-2">
          {policy.claim_requirements?.documents_required?.map((r: string, i: number) => (
            <div key={i} className="flex items-center gap-2 text-sm p-2 rounded-lg bg-surface">
              <span className="text-accent-green">✓</span> {r}
            </div>
          ))}
          <div className="mt-3 grid grid-cols-2 gap-3">
            <Stat label="Submission Deadline" value={`${policy.claim_requirements?.submission_timeline_days} days`} />
            <Stat label="Minimum Amount" value={`₹${policy.claim_requirements?.minimum_claim_amount}`} />
          </div>
        </div>
      ),
    },
    {
      key: "network",
      title: "Network Hospitals",
      icon: Shield,
      content: (
        <div className="grid grid-cols-2 gap-2">
          {policy.network_hospitals?.map((h: string) => (
            <div key={h} className="bg-surface p-3 rounded-lg text-sm flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-accent-green" /> {h}
            </div>
          ))}
        </div>
      ),
    },
  ];

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      <h1 className="text-2xl font-bold mb-2"><span className="gradient-text">{policy.policy_name}</span></h1>
      <p className="text-text-secondary text-sm mb-8">Policy ID: {policy.policy_id} — Effective: {policy.effective_date}</p>

      <div className="space-y-3">
        {sections.map((s) => (
          <div key={s.key} className="glass-card overflow-hidden">
            <button onClick={() => toggle(s.key)} className="w-full flex items-center justify-between p-5 hover:bg-surface-elevated/30 transition-colors">
              <div className="flex items-center gap-3">
                <s.icon size={18} className="text-plum-400" />
                <span className="font-semibold">{s.title}</span>
              </div>
              {expanded.includes(s.key) ? <ChevronDown size={18} className="text-text-muted" /> : <ChevronRight size={18} className="text-text-muted" />}
            </button>
            {expanded.includes(s.key) && <div className="px-5 pb-5">{s.content}</div>}
          </div>
        ))}
      </div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-surface p-3 rounded-lg">
      <p className="text-xs text-text-muted">{label}</p>
      <p className="font-bold">{value}</p>
    </div>
  );
}
