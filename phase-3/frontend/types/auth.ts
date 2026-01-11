/**
 * Authentication Type Definitions
 * Matches backend API contracts
 *
 * Spec Reference: specs/api/rest-endpoints.md
 */

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface RegisterResponse {
  id: number;
  email: string;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface ErrorResponse {
  detail: string | ValidationError[];
}

export interface ValidationError {
  loc: string[];
  msg: string;
  type: string;
}

export interface User {
  id: number;
  email: string;
  name: string | null;
  profile_picture: string | null;
  created_at: string;
}

export interface ProfileUpdateRequest {
  name?: string | null;
  profile_picture?: string | null;
}
