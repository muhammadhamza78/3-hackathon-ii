// <<<<<<< HEAD
// /**
//  * Authentication Client
//  * Handles user login and token management
//  */

// import { apiPost } from "@/lib/api";
// import type { User } from "@/types/auth";

// export interface LoginResponse {
//   access_token: string;
//   token_type: string;
//   expires_in: number;
//   user: {
//     id: number;
//     email: string;
//     name: string | null;
//     profile_picture: string | null;
//   };
// }

// export async function loginUser(email: string, password: string): Promise<LoginResponse> {
//   const res = await apiPost("/api/auth/login", { email, password }, false);

//   if (!res.ok) {
//     const err = await res.json().catch(() => ({}));
//     throw new Error(err?.detail || "Login failed");
//   }

//   const data: LoginResponse = await res.json();

//   if (typeof window !== "undefined") {
//     // Store JWT token and expiry
//     localStorage.setItem("jwt_token", data.access_token);
//     const expiryTime = Date.now() + data.expires_in * 1000;
//     localStorage.setItem("token_expiry", expiryTime.toString());

//     // Store user data for quick access (optional but helpful)
//     localStorage.setItem("user_data", JSON.stringify({
//       id: data.user.id,
//       email: data.user.email,
//       name: data.user.name,
//       profile_picture: data.user.profile_picture
//     }));
//   }

//   return data;
// }
// =======
// const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// export interface User {
//   id: number;
//   email: string;
// }

// export interface LoginResponse {
//   access_token: string;
//   token_type: string;
//   expires_in: number;
// }

// export interface RegisterData {
//   email: string;
//   password: string;
// }

// export interface LoginData {
//   email: string;
//   password: string;
// }

// async function register(data: RegisterData): Promise<User> {
//   const response = await fetch(`${API_URL}/api/auth/register`, {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify(data),
//   });

//   if (!response.ok) {
//     const error = await response.json();
//     throw new Error(error.detail || "Registration failed");
//   }

//   return response.json();
// }

// async function login(data: LoginData): Promise<LoginResponse> {
//   const response = await fetch(`${API_URL}/api/auth/login`, {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify(data),
//   });

//   if (!response.ok) {
//     const error = await response.json();
//     throw new Error(error.detail || "Login failed");
//   }

//   const tokenData = await response.json();

//   if (typeof window !== "undefined") {
//     localStorage.setItem("access_token", tokenData.access_token);
//     localStorage.setItem("token_type", tokenData.token_type);
//   }

//   return tokenData;
// }

// function logout(): void {
//   if (typeof window !== "undefined") {
//     localStorage.removeItem("access_token");
//     localStorage.removeItem("token_type");
//   }
// }

// function getAccessToken(): string | null {
//   if (typeof window !== "undefined") {
//     return localStorage.getItem("access_token");
//   }
//   return null;
// }

// function isAuthenticated(): boolean {
//   return getAccessToken() !== null;
// }

// function getAuthHeader(): Record<string, string> {
//   const token = getAccessToken();
//   if (token) return { Authorization: `Bearer ${token}` };
//   return {};
// }

// export const auth = {
//   register,
//   login,
//   logout,
//   getAccessToken,
//   isAuthenticated,
//   getAuthHeader,
// };
// >>>>>>> 09fec55ab4658b42257e6db6376aa6c6353809ac











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
    // Store JWT token and expiry
    localStorage.setItem("jwt_token", data.access_token);
    const expiryTime = Date.now() + data.expires_in * 1000;
    localStorage.setItem("token_expiry", expiryTime.toString());

    // Store user data
    localStorage.setItem("user_data", JSON.stringify({
      id: data.user.id,
      email: data.user.email,
      name: data.user.name,
      profile_picture: data.user.profile_picture
    }));
  }

  return data;
}

