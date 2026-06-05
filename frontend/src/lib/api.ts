const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiFetch(path: string, options?: RequestInit) {
  const res = await fetch(`${API}${path}`, {
    ...options,
    headers: { ...options?.headers },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "API Error");
  }
  return res.json();
}

export async function apiPost(path: string, body: FormData | object) {
  const isForm = body instanceof FormData;
  const res = await fetch(`${API}${path}`, {
    method: "POST",
    body: isForm ? body : JSON.stringify(body),
    headers: isForm ? {} : { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "API Error");
  }
  return res.json();
}

export async function apiPut(path: string, body: FormData | object) {
  const isForm = body instanceof FormData;
  const res = await fetch(`${API}${path}`, {
    method: "PUT",
    body: isForm ? body : JSON.stringify(body),
    headers: isForm ? {} : { "Content-Type": "application/json" },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "API Error");
  }
  return res.json();
}

export function getDocumentUrl(claimId: string, fileId: string) {
  return `${API}/api/claims/${claimId}/documents/${fileId}`;
}
