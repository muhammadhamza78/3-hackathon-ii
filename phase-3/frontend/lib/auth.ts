/**
 * Authentication Client
 * Handles user login and token management
 */

import { apiPost } from "@/lib/api";

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: number;
    email: string;
    name: string | null;
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

  if (typeof window !== "undefined") {
    localStorage.setItem("jwt_token", data.access_token);
    const expiryTime = Date.now() + data.expires_in * 1000;
    localStorage.setItem("token_expiry", expiryTime.toString());
    localStorage.setItem("user_data", JSON.stringify({
      id: data.user.id,
      email: data.user.email,
      name: data.user.name,
      profile_picture: data.user.profile_picture
    }));
  }

  return data;
}

export function logout(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem("jwt_token");
    localStorage.removeItem("token_expiry");
    localStorage.removeItem("user_data");
  }
}

export function getAccessToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem("jwt_token");
  }
  return null;
}

export function isAuthenticated(): boolean {
  return getAccessToken() !== null;
}

export function getAuthHeader(): Record<string, string> {
  const token = getAccessToken();
  if (token) return { Authorization: `Bearer ${token}` };
  return {};
}

// Export auth object for better-auth compatibility
export const auth = {
  loginUser,
  logout,
  getAccessToken,
  isAuthenticated,
  getAuthHeader,
};

