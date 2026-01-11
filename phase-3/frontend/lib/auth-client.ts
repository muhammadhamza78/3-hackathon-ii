import { apiPost } from "@/lib/api"; // your fetch wrapper

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
  const expiryTime = Date.now() + data.expires_in * 1000;
  localStorage.setItem("token_expiry", expiryTime.toString());

  return data;
}
