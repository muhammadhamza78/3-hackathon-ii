// frontend/lib/api.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL;

export async function apiGet(url: string) {
  return fetch(`${API_BASE}${url}`);
}
