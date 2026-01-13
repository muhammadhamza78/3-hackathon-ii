// lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://3-hackathon-ii-production.up.railway.app";

// ---------------- GET ----------------
export async function apiGet(url: string, requiresAuth: boolean = true): Promise<Response> {
  const headers: HeadersInit = {};

  if (requiresAuth && typeof window !== "undefined") {
    const token = localStorage.getItem("jwt_token");
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  return fetch(`${API_BASE}${url}`, {
    method: "GET",
    headers,
  });
}

// ---------------- POST ----------------
export async function apiPost(url: string, body?: any, requiresAuth: boolean = true): Promise<Response> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };

  if (requiresAuth && typeof window !== "undefined") {
    const token = localStorage.getItem("jwt_token");
    if (token) headers.Authorization = `Bearer ${token}`;
  }

return fetch(`${API_BASE}${url}`, {
  method: "POST",
  headers,
  body: JSON.stringify(body || {}),
  credentials: "include", // ✅ ADD THIS
});

}


// ---------------- PUT ----------------
export async function apiPut(url: string, body?: any, requiresAuth: boolean = true): Promise<Response> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };

  if (requiresAuth && typeof window !== "undefined") {
    const token = localStorage.getItem("jwt_token");
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  return fetch(`${API_BASE}${url}`, {
    method: "PUT",
    headers,
    body: JSON.stringify(body || {}),
  });
}

// ---------------- DELETE ----------------
export async function apiDelete(url: string, requiresAuth: boolean = true): Promise<Response> {
  const headers: HeadersInit = {};

  if (requiresAuth && typeof window !== "undefined") {
    const token = localStorage.getItem("jwt_token");
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  return fetch(`${API_BASE}${url}`, {
    method: "DELETE",
    headers,
  });
}

// ---------------- Login ----------------
export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    email: string;
    name: string;
    profile_picture: string | null;
  };
}

export async function loginUser(email: string, password: string): Promise<LoginResponse> {
  const res = await apiPost("/api/auth/login", { email, password }, false);

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail || "Login failed");
  }

  const data: LoginResponse = await res.json();

  localStorage.setItem("jwt_token", data.access_token);
  localStorage.setItem("token_expiry", (Date.now() + data.expires_in * 1000).toString());

  return {
    ...data,
    user: {
      ...data.user,
      name: data.user.name || "",
      profile_picture: data.user.profile_picture || null,
    },
  };
}

// ---------------- Task History ----------------
// ---------------- Task History ----------------
export async function getTaskHistory() {
  const res = await apiGet("/api/tasks/history", true);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.detail || `Failed to fetch task history (${res.status})`);
  }
  const data = await res.json();
  return data.tasks || []; // ensure array return
}

export async function restoreTask(taskId: number) {
  const res = await apiPost(`/api/tasks/${taskId}/restore`, {}, true);
  if (!res.ok) throw new Error("Failed to restore task");
  return res.json();
}

export async function clearTaskHistory() {
  const res = await apiDelete("/api/tasks/history", true);
  if (!res.ok) throw new Error("Failed to clear task history");
  return true;
}


// ---------------- Clear Completed Tasks ----------------
export async function clearCompletedTasks() {
  const res = await apiPost("/api/tasks/clear-completed", {}, true);
  if (!res.ok) throw new Error("Failed to clear completed tasks");
  return true;
}


