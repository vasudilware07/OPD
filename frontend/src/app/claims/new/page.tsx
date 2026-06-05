"use client";
import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useDropzone } from "react-dropzone";
import { apiFetch } from "@/lib/api";
import {
  Upload, FileText, User, Calendar, DollarSign, Building2,
  CheckCircle, AlertTriangle, Loader2, X, Image as ImageIcon
} from "lucide-react";

interface Member { member_id: string; name: string; email: string; }

export default function NewClaimPage() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [members, setMembers] = useState<Member[]>([]);
  const [files, setFiles] = useState<File[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<any>(null);

  const [form, setForm] = useState({
    member_id: "",
    member_name: "",
    treatment_date: "",
    claim_amount: "",
    hospital_name: "",
    cashless_request: false,
    description: "",
  });

  useEffect(() => {
    apiFetch("/api/members?limit=100").then((d) => setMembers(d.members || [])).catch(() => {});
  }, []);

  const onDrop = useCallback((accepted: File[]) => {
    setFiles((prev) => [...prev, ...accepted]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "image/*": [".jpg", ".jpeg", ".png", ".webp"], "application/pdf": [".pdf"] },
    maxSize: 10 * 1024 * 1024,
  });

  const removeFile = (i: number) => setFiles((prev) => prev.filter((_, idx) => idx !== i));

  const handleMemberSelect = (id: string) => {
    const m = members.find((m) => m.member_id === id);
    setForm({ ...form, member_id: id, member_name: m?.name || "" });
  };

  const handleSubmit = async () => {
    if (!form.member_id || !form.treatment_date || !form.claim_amount || files.length === 0) {
      setError("Please fill all required fields and upload at least one document.");
      return;
    }
    setSubmitting(true);
    setError("");

    const fd = new FormData();
    fd.append("member_id", form.member_id);
    fd.append("member_name", form.member_name);
    fd.append("treatment_date", form.treatment_date);
    fd.append("claim_amount", form.claim_amount);
    if (form.hospital_name) fd.append("hospital_name", form.hospital_name);
    fd.append("cashless_request", String(form.cashless_request));
    if (form.description) fd.append("description", form.description);
    files.forEach((f) => fd.append("documents", f));

    try {
      const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${API}/api/claims`, { method: "POST", body: fd });
      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Submission failed" }));
        throw new Error(err.detail);
      }
      const data = await res.json();
      setResult(data);
      setStep(4);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setSubmitting(false);
    }
  };

  const statusColor: Record<string, string> = {
    APPROVED: "text-accent-green",
    REJECTED: "text-accent-red",
    PARTIAL: "text-accent-yellow",
    MANUAL_REVIEW: "text-accent-blue",
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      <h1 className="text-2xl font-bold mb-2">
        <span className="gradient-text">Submit New Claim</span>
      </h1>
      <p className="text-text-secondary text-sm mb-8">Upload documents and get an instant AI-powered decision</p>

      {/* Progress Steps */}
      <div className="flex items-center gap-2 mb-10">
        {["Member", "Details", "Documents", "Result"].map((label, i) => (
          <div key={label} className="flex items-center gap-2 flex-1">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-all ${
              step > i + 1 ? "bg-accent-green text-white" : step === i + 1 ? "bg-plum-600 text-white" : "bg-surface-elevated text-text-muted"
            }`}>
              {step > i + 1 ? <CheckCircle size={16} /> : i + 1}
            </div>
            <span className={`text-xs font-medium ${step >= i + 1 ? "text-text-primary" : "text-text-muted"}`}>{label}</span>
            {i < 3 && <div className={`flex-1 h-px ${step > i + 1 ? "bg-accent-green" : "bg-surface-border"}`} />}
          </div>
        ))}
      </div>

      {error && (
        <div className="mb-6 p-4 rounded-xl bg-accent-red/10 border border-accent-red/30 text-accent-red flex items-center gap-3 text-sm">
          <AlertTriangle size={18} /> {error}
        </div>
      )}

      {/* Step 1: Member Selection */}
      {step === 1 && (
        <div className="glass-card p-8 animate-fade-in">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><User size={20} className="text-plum-400" /> Select Member</h2>
          <select
            className="input-field mb-4"
            value={form.member_id}
            onChange={(e) => handleMemberSelect(e.target.value)}
          >
            <option value="">-- Select a member --</option>
            {members.map((m) => (
              <option key={m.member_id} value={m.member_id}>{m.member_id} — {m.name}</option>
            ))}
          </select>
          {form.member_id && (
            <div className="p-4 rounded-xl bg-surface text-sm text-text-secondary">
              Selected: <span className="text-text-primary font-medium">{form.member_name}</span> ({form.member_id})
            </div>
          )}
          <div className="mt-6 flex justify-end">
            <button className="btn-primary" onClick={() => form.member_id && setStep(2)} disabled={!form.member_id}>
              Next: Treatment Details
            </button>
          </div>
        </div>
      )}

      {/* Step 2: Treatment Details */}
      {step === 2 && (
        <div className="glass-card p-8 animate-fade-in">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Calendar size={20} className="text-plum-400" /> Treatment Details</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-text-muted font-medium mb-1 block">Treatment Date *</label>
              <input type="date" className="input-field" value={form.treatment_date} onChange={(e) => setForm({ ...form, treatment_date: e.target.value })} />
            </div>
            <div>
              <label className="text-xs text-text-muted font-medium mb-1 block">Claim Amount (₹) *</label>
              <input type="number" className="input-field" placeholder="e.g., 1500" value={form.claim_amount} onChange={(e) => setForm({ ...form, claim_amount: e.target.value })} />
            </div>
            <div>
              <label className="text-xs text-text-muted font-medium mb-1 block">Hospital / Clinic Name</label>
              <input type="text" className="input-field" placeholder="e.g., Apollo Hospitals" value={form.hospital_name} onChange={(e) => setForm({ ...form, hospital_name: e.target.value })} />
            </div>
            <div className="flex items-end">
              <label className="flex items-center gap-2 cursor-pointer">
                <input type="checkbox" checked={form.cashless_request} onChange={(e) => setForm({ ...form, cashless_request: e.target.checked })} className="w-4 h-4 accent-plum-500" />
                <span className="text-sm">Cashless Request</span>
              </label>
            </div>
          </div>
          <div className="mt-4">
            <label className="text-xs text-text-muted font-medium mb-1 block">Description (optional)</label>
            <textarea className="input-field h-20" placeholder="Brief description of the treatment..." value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </div>
          <div className="mt-6 flex justify-between">
            <button className="btn-secondary" onClick={() => setStep(1)}>Back</button>
            <button className="btn-primary" onClick={() => form.treatment_date && form.claim_amount && setStep(3)}>Next: Upload Documents</button>
          </div>
        </div>
      )}

      {/* Step 3: Document Upload */}
      {step === 3 && (
        <div className="glass-card p-8 animate-fade-in">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Upload size={20} className="text-plum-400" /> Upload Documents</h2>
          <p className="text-text-secondary text-sm mb-4">Upload prescriptions, bills, and diagnostic reports (images or PDFs)</p>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all ${
              isDragActive ? "border-plum-400 bg-plum-600/10" : "border-surface-border hover:border-plum-500/50"
            }`}
          >
            <input {...getInputProps()} />
            <Upload size={40} className="mx-auto mb-3 text-text-muted" />
            <p className="text-text-primary font-medium">
              {isDragActive ? "Drop files here..." : "Drag & drop files, or click to browse"}
            </p>
            <p className="text-text-muted text-xs mt-1">JPG, PNG, PDF — Max 10MB each</p>
          </div>

          {files.length > 0 && (
            <div className="mt-4 space-y-2">
              {files.map((f, i) => (
                <div key={i} className="flex items-center justify-between bg-surface p-3 rounded-lg">
                  <div className="flex items-center gap-3">
                    {f.type.startsWith("image/") ? <ImageIcon size={16} className="text-plum-400" /> : <FileText size={16} className="text-plum-400" />}
                    <span className="text-sm">{f.name}</span>
                    <span className="text-xs text-text-muted">({(f.size / 1024).toFixed(1)} KB)</span>
                  </div>
                  <button onClick={() => removeFile(i)} className="text-text-muted hover:text-accent-red"><X size={16} /></button>
                </div>
              ))}
            </div>
          )}

          <div className="mt-6 flex justify-between">
            <button className="btn-secondary" onClick={() => setStep(2)}>Back</button>
            <button className="btn-primary flex items-center gap-2" onClick={handleSubmit} disabled={submitting || files.length === 0}>
              {submitting ? <><Loader2 size={18} className="animate-spin" /> Processing with AI...</> : "Submit & Adjudicate"}
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Result */}
      {step === 4 && result && (
        <div className="animate-fade-in space-y-6">
          <div className="glass-card p-8 text-center">
            <div className={`text-4xl font-bold mb-2 ${statusColor[result.claim?.status] || "text-text-primary"}`}>
              {result.claim?.status?.replace("_", " ")}
            </div>
            <p className="text-text-secondary">{result.message}</p>
            {result.claim?.decision?.approved_amount > 0 && (
              <p className="text-2xl font-bold text-accent-green mt-2">
                ₹{result.claim.decision.approved_amount.toLocaleString("en-IN")} Approved
              </p>
            )}
            {result.claim?.decision?.confidence_score && (
              <div className="mt-4 max-w-xs mx-auto">
                <p className="text-xs text-text-muted mb-1">AI Confidence</p>
                <div className="w-full bg-surface rounded-full h-3">
                  <div className="h-3 rounded-full bg-gradient-to-r from-plum-600 to-plum-400 transition-all" style={{ width: `${result.claim.decision.confidence_score * 100}%` }} />
                </div>
                <p className="text-xs text-text-secondary mt-1">{(result.claim.decision.confidence_score * 100).toFixed(0)}%</p>
              </div>
            )}
          </div>

          {/* Decision Details */}
          {result.claim?.decision && (
            <div className="glass-card p-6">
              <h3 className="font-semibold mb-3">Decision Details</h3>
              {result.claim.decision.reasoning && (
                <pre className="text-xs text-text-secondary bg-surface p-4 rounded-lg whitespace-pre-wrap mb-4">{result.claim.decision.reasoning}</pre>
              )}
              {result.claim.decision.rejection_reasons?.length > 0 && (
                <div className="mb-3">
                  <p className="text-xs text-text-muted font-medium mb-1">Rejection Reasons:</p>
                  <div className="flex flex-wrap gap-2">
                    {result.claim.decision.rejection_reasons.map((r: string) => (
                      <span key={r} className="status-rejected px-2 py-1 rounded text-xs">{r}</span>
                    ))}
                  </div>
                </div>
              )}
              {result.claim.decision.next_steps && (
                <p className="text-sm text-text-secondary mt-3">
                  <span className="font-medium text-text-primary">Next Steps: </span>{result.claim.decision.next_steps}
                </p>
              )}
            </div>
          )}

          {/* Rule Checks */}
          {result.claim?.decision?.rule_checks?.length > 0 && (
            <div className="glass-card p-6">
              <h3 className="font-semibold mb-3">Rule Checks</h3>
              <div className="space-y-2">
                {result.claim.decision.rule_checks.map((r: any, i: number) => (
                  <div key={i} className="flex items-center gap-3 text-sm p-2 rounded-lg bg-surface">
                    <span className={r.status === "PASS" ? "text-accent-green" : "text-accent-red"}>
                      {r.status === "PASS" ? "✓" : "✗"}
                    </span>
                    <span className="font-medium min-w-[160px]">{r.rule}</span>
                    <span className="text-text-secondary">{r.detail}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex gap-3">
            <button className="btn-primary" onClick={() => router.push(`/claims/${result.claim?.claim_id}`)}>View Full Details</button>
            <button className="btn-secondary" onClick={() => { setStep(1); setForm({ member_id: "", member_name: "", treatment_date: "", claim_amount: "", hospital_name: "", cashless_request: false, description: "" }); setFiles([]); setResult(null); }}>Submit Another</button>
          </div>
        </div>
      )}
    </div>
  );
}
