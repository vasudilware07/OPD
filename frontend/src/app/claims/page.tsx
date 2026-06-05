"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";
import { Search, Filter, Eye, ChevronLeft, ChevronRight } from "lucide-react";

function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    APPROVED: "status-approved", REJECTED: "status-rejected",
    PARTIAL: "status-partial", MANUAL_REVIEW: "status-review",
    PENDING: "status-pending", APPEALED: "status-review",
  };
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${map[status] || "status-pending"}`}>
      {status.replace("_", " ")}
    </span>
  );
}

export default function ClaimsListPage() {
  const [claims, setClaims] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [statusFilter, setStatusFilter] = useState("");
  const [loading, setLoading] = useState(true);

  const fetchClaims = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page: String(page), limit: "15" });
      if (statusFilter) params.set("status", statusFilter);
      const data = await apiFetch(`/api/claims?${params}`);
      setClaims(data.claims || []);
      setTotal(data.total || 0);
      setTotalPages(data.total_pages || 1);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchClaims(); }, [page, statusFilter]);

  const statuses = ["", "APPROVED", "REJECTED", "PARTIAL", "MANUAL_REVIEW", "PENDING", "APPEALED"];

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold"><span className="gradient-text">All Claims</span></h1>
          <p className="text-text-secondary text-sm">{total} total claims</p>
        </div>
        <Link href="/claims/new" className="btn-primary">+ New Claim</Link>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 mb-6">
        <Filter size={16} className="text-text-muted" />
        {statuses.map((s) => (
          <button
            key={s}
            onClick={() => { setStatusFilter(s); setPage(1); }}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              statusFilter === s ? "bg-plum-600 text-white" : "bg-surface-elevated text-text-secondary hover:text-text-primary"
            }`}
          >
            {s || "All"}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="glass-card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-surface-border text-text-muted text-xs uppercase tracking-wider">
              <th className="text-left py-3 px-4">Claim ID</th>
              <th className="text-left py-3 px-4">Member</th>
              <th className="text-left py-3 px-4">Treatment Date</th>
              <th className="text-right py-3 px-4">Amount</th>
              <th className="text-center py-3 px-4">Status</th>
              <th className="text-right py-3 px-4">Approved</th>
              <th className="text-center py-3 px-4">Confidence</th>
              <th className="text-center py-3 px-4">Docs</th>
              <th className="text-center py-3 px-4">Action</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={9} className="py-12 text-center text-text-muted">Loading...</td></tr>
            ) : claims.length === 0 ? (
              <tr><td colSpan={9} className="py-12 text-center text-text-muted">No claims found</td></tr>
            ) : claims.map((c) => (
              <tr key={c.claim_id} className="border-b border-surface-border/50 hover:bg-surface-elevated/50 transition-colors">
                <td className="py-3 px-4 font-mono text-plum-400 text-xs">{c.claim_id}</td>
                <td className="py-3 px-4">{c.member_name}</td>
                <td className="py-3 px-4 text-text-secondary">{c.treatment_date}</td>
                <td className="py-3 px-4 text-right">₹{c.claim_amount?.toLocaleString("en-IN")}</td>
                <td className="py-3 px-4 text-center"><StatusBadge status={c.status} /></td>
                <td className="py-3 px-4 text-right text-accent-green font-medium">₹{(c.decision?.approved_amount || 0).toLocaleString("en-IN")}</td>
                <td className="py-3 px-4 text-center">
                  <span className="text-xs text-text-secondary">{((c.decision?.confidence_score || 0) * 100).toFixed(0)}%</span>
                </td>
                <td className="py-3 px-4 text-center text-text-secondary">{c.documents?.length || 0}</td>
                <td className="py-3 px-4 text-center">
                  <Link href={`/claims/${c.claim_id}`} className="text-plum-400 hover:text-plum-300"><Eye size={16} /></Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-surface-border">
            <p className="text-xs text-text-muted">Page {page} of {totalPages}</p>
            <div className="flex gap-2">
              <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="btn-secondary text-xs px-3 py-1"><ChevronLeft size={14} /></button>
              <button onClick={() => setPage(Math.min(totalPages, page + 1))} disabled={page === totalPages} className="btn-secondary text-xs px-3 py-1"><ChevronRight size={14} /></button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
