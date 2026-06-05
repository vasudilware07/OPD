"use client";
import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiFetch, getDocumentUrl } from "@/lib/api";
import {
  FileText, CheckCircle, XCircle, AlertTriangle, Clock, Shield,
  ArrowLeft, MessageSquare, Loader2, Eye
} from "lucide-react";
import Link from "next/link";

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, { cls: string; icon: any }> = {
    APPROVED: { cls: "status-approved", icon: CheckCircle },
    REJECTED: { cls: "status-rejected", icon: XCircle },
    PARTIAL: { cls: "status-partial", icon: AlertTriangle },
    MANUAL_REVIEW: { cls: "status-review", icon: Clock },
    PENDING: { cls: "status-pending", icon: Clock },
    APPEALED: { cls: "status-review", icon: MessageSquare },
  };
  const entry = map[status] || map.PENDING;
  const Icon = entry.icon;
  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold ${entry.cls}`}>
      <Icon size={14} /> {status.replace("_", " ")}
    </span>
  );
}

export default function ClaimDetailPage() {
  const params = useParams();
  const claimId = params.id as string;
  const [claim, setClaim] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [appealReason, setAppealReason] = useState("");
  const [appealing, setAppealing] = useState(false);
  const [showAppealForm, setShowAppealForm] = useState(false);

  useEffect(() => {
    apiFetch(`/api/claims/${claimId}`)
      .then(setClaim)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [claimId]);

  const handleAppeal = async () => {
    if (!appealReason.trim()) return;
    setAppealing(true);
    try {
      const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const fd = new FormData();
      fd.append("reason", appealReason);
      const res = await fetch(`${API}/api/claims/${claimId}/appeal`, { method: "PUT", body: fd });
      if (res.ok) {
        const updated = await apiFetch(`/api/claims/${claimId}`);
        setClaim(updated);
        setShowAppealForm(false);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setAppealing(false);
    }
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center"><Loader2 size={32} className="animate-spin text-plum-400" /></div>;
  if (!claim) return <div className="max-w-4xl mx-auto px-6 py-12 text-center text-text-muted">Claim not found</div>;

  const d = claim.decision || {};

  return (
    <div className="max-w-5xl mx-auto px-6 py-8">
      <Link href="/claims" className="text-text-secondary hover:text-text-primary text-sm flex items-center gap-1 mb-6">
        <ArrowLeft size={14} /> Back to Claims
      </Link>

      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-3">
            <span className="font-mono text-plum-400">{claim.claim_id}</span>
            <StatusBadge status={claim.status} />
          </h1>
          <p className="text-text-secondary mt-1">{claim.member_name} ({claim.member_id}) — {claim.treatment_date}</p>
        </div>
        <div className="text-right">
          <p className="text-xs text-text-muted">Claim Amount</p>
          <p className="text-xl font-bold">₹{claim.claim_amount?.toLocaleString("en-IN")}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Decision */}
        <div className="lg:col-span-2 space-y-6">
          {/* Decision Card */}
          <div className="glass-card p-6">
            <h2 className="font-semibold mb-4 flex items-center gap-2"><Shield size={18} className="text-plum-400" /> AI Decision</h2>
            <div className="grid grid-cols-3 gap-4 mb-4">
              <div className="bg-surface p-3 rounded-lg text-center">
                <p className="text-xs text-text-muted">Approved</p>
                <p className="text-lg font-bold text-accent-green">₹{(d.approved_amount || 0).toLocaleString("en-IN")}</p>
              </div>
              <div className="bg-surface p-3 rounded-lg text-center">
                <p className="text-xs text-text-muted">Confidence</p>
                <p className="text-lg font-bold text-plum-400">{((d.confidence_score || 0) * 100).toFixed(0)}%</p>
              </div>
              <div className="bg-surface p-3 rounded-lg text-center">
                <p className="text-xs text-text-muted">Deductions</p>
                <p className="text-lg font-bold text-accent-yellow">₹{Object.values(d.deductions || {}).reduce((a: number, b: any) => a + (Number(b) || 0), 0).toLocaleString("en-IN")}</p>
              </div>
            </div>

            {/* Confidence Bar */}
            <div className="mb-4">
              <div className="w-full bg-surface rounded-full h-2.5">
                <div className="h-2.5 rounded-full bg-gradient-to-r from-plum-600 to-plum-400 transition-all duration-700" style={{ width: `${(d.confidence_score || 0) * 100}%` }} />
              </div>
            </div>

            {/* Reasoning */}
            {d.reasoning && (
              <div className="mb-4">
                <p className="text-xs text-text-muted font-medium mb-1">AI Reasoning</p>
                <pre className="text-xs text-text-secondary bg-surface p-4 rounded-lg whitespace-pre-wrap max-h-60 overflow-y-auto">{d.reasoning}</pre>
              </div>
            )}

            {/* Rejection Reasons */}
            {d.rejection_reasons?.length > 0 && (
              <div className="mb-4">
                <p className="text-xs text-text-muted font-medium mb-1">Rejection Reasons</p>
                <div className="flex flex-wrap gap-2">
                  {d.rejection_reasons.map((r: string) => (
                    <span key={r} className="status-rejected px-2 py-1 rounded text-xs font-mono">{r}</span>
                  ))}
                </div>
              </div>
            )}

            {/* Next Steps */}
            {d.next_steps && (
              <div className="p-3 rounded-lg bg-plum-600/10 border border-plum-600/20 text-sm text-text-secondary">
                <span className="font-medium text-plum-300">Next Steps: </span>{d.next_steps}
              </div>
            )}
          </div>

          {/* Rule Checks */}
          {d.rule_checks?.length > 0 && (
            <div className="glass-card p-6">
              <h2 className="font-semibold mb-4">Rule Check Results</h2>
              <div className="space-y-2">
                {d.rule_checks.map((r: any, i: number) => (
                  <div key={i} className="flex items-center gap-3 text-sm p-2.5 rounded-lg bg-surface">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${r.status === "PASS" ? "bg-accent-green/20 text-accent-green" : "bg-accent-red/20 text-accent-red"}`}>
                      {r.status === "PASS" ? "✓" : "✗"}
                    </div>
                    <span className="font-medium min-w-[180px]">{r.rule}</span>
                    <span className="text-text-secondary flex-1">{r.detail}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Appeal Section */}
          {(claim.status === "REJECTED" || claim.status === "PARTIAL") && !claim.appeal && (
            <div className="glass-card p-6">
              {!showAppealForm ? (
                <button className="btn-secondary w-full" onClick={() => setShowAppealForm(true)}>
                  <MessageSquare size={16} className="inline mr-2" /> Appeal This Decision
                </button>
              ) : (
                <div>
                  <h3 className="font-semibold mb-3">Submit Appeal</h3>
                  <textarea className="input-field h-24 mb-3" placeholder="Explain why you believe this decision should be reconsidered..." value={appealReason} onChange={(e) => setAppealReason(e.target.value)} />
                  <div className="flex gap-2">
                    <button className="btn-primary flex items-center gap-2" onClick={handleAppeal} disabled={appealing}>
                      {appealing ? <Loader2 size={16} className="animate-spin" /> : null} Submit Appeal
                    </button>
                    <button className="btn-secondary" onClick={() => setShowAppealForm(false)}>Cancel</button>
                  </div>
                </div>
              )}
            </div>
          )}
          {claim.appeal && (
            <div className="glass-card p-6">
              <h3 className="font-semibold mb-2 flex items-center gap-2"><MessageSquare size={16} className="text-accent-blue" /> Appeal Submitted</h3>
              <p className="text-sm text-text-secondary mb-1"><strong>Reason:</strong> {claim.appeal.reason}</p>
              <p className="text-xs text-text-muted">Status: {claim.appeal.appeal_status} — Submitted {claim.appeal.appealed_at}</p>
            </div>
          )}
        </div>

        {/* Right: Documents & Extraction */}
        <div className="space-y-6">
          {/* Documents */}
          <div className="glass-card p-5">
            <h3 className="font-semibold mb-3 flex items-center gap-2"><FileText size={16} className="text-plum-400" /> Documents ({claim.documents?.length || 0})</h3>
            <div className="space-y-2">
              {claim.documents?.map((doc: any) => (
                <a key={doc.file_id} href={getDocumentUrl(claimId, doc.file_id)} target="_blank" rel="noopener noreferrer"
                  className="flex items-center gap-3 p-2.5 rounded-lg bg-surface hover:bg-surface-elevated transition-colors"
                >
                  <Eye size={14} className="text-plum-400" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm truncate">{doc.original_name}</p>
                    <p className="text-xs text-text-muted">{(doc.size / 1024).toFixed(1)} KB</p>
                  </div>
                </a>
              ))}
            </div>
          </div>

          {/* Extraction Results */}
          {claim.extraction_results?.length > 0 && (
            <div className="glass-card p-5">
              <h3 className="font-semibold mb-3">AI Extraction</h3>
              {claim.extraction_results.map((ext: any, i: number) => (
                <div key={i} className="mb-4 last:mb-0">
                  <p className="text-xs text-plum-400 font-medium mb-2 uppercase">{ext.document_type || "Document"} {i + 1}</p>
                  <div className="space-y-1 text-xs">
                    {ext.patient_name && <div className="flex justify-between"><span className="text-text-muted">Patient</span><span>{ext.patient_name}</span></div>}
                    {ext.doctor_name && <div className="flex justify-between"><span className="text-text-muted">Doctor</span><span>{ext.doctor_name}</span></div>}
                    {ext.doctor_registration && <div className="flex justify-between"><span className="text-text-muted">Reg. No</span><span className="font-mono">{ext.doctor_registration}</span></div>}
                    {ext.diagnosis && <div className="flex justify-between"><span className="text-text-muted">Diagnosis</span><span>{ext.diagnosis}</span></div>}
                    {ext.total_amount && <div className="flex justify-between"><span className="text-text-muted">Amount</span><span>₹{ext.total_amount}</span></div>}
                    <div className="flex justify-between"><span className="text-text-muted">Confidence</span><span>{((ext.confidence || 0) * 100).toFixed(0)}%</span></div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Claim Info */}
          <div className="glass-card p-5">
            <h3 className="font-semibold mb-3">Claim Info</h3>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between"><span className="text-text-muted">Created</span><span>{claim.created_at}</span></div>
              {claim.hospital_name && <div className="flex justify-between"><span className="text-text-muted">Hospital</span><span>{claim.hospital_name}</span></div>}
              <div className="flex justify-between"><span className="text-text-muted">Cashless</span><span>{claim.cashless_request ? "Yes" : "No"}</span></div>
              {d.network_discount > 0 && <div className="flex justify-between"><span className="text-text-muted">Network Discount</span><span className="text-accent-green">₹{d.network_discount}</span></div>}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
