/**
 * Profile API Client
 * Handles user profile operations
 *
 * Spec: specs/002-dashboard-ux-enhancements/spec.md (FR-001, FR-002, FR-003)
 */

import { User, ProfileUpdateRequest } from "@/types/auth";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Get current user's profile
 */
export async function getProfile(): Promise<User> {
  const token = localStorage.getItem("jwt_token");

  if (!token) {
    throw new Error("Not authenticated");
  }

  const response = await fetch(`${API_BASE}/api/v1/profile`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to fetch profile" }));
    throw new Error(error.detail || "Failed to fetch profile");
  }

  return response.json();
}

/**
 * Update user profile (name and/or profile picture URL)
 */
export async function updateProfile(data: ProfileUpdateRequest): Promise<User> {
  const token = localStorage.getItem("jwt_token");

  if (!token) {
    throw new Error("Not authenticated");
  }

  const response = await fetch(`${API_BASE}/api/v1/profile`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to update profile" }));
    throw new Error(error.detail || "Failed to update profile");
  }

  return response.json();
}

/**
 * Upload profile picture to cloud storage
 */
export async function uploadProfilePicture(file: File): Promise<User> {
  const token = localStorage.getItem("jwt_token");

  if (!token) {
    throw new Error("Not authenticated");
  }

  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE}/api/v1/profile/upload-picture`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to upload picture" }));
    throw new Error(error.detail || "Failed to upload picture");
  }

  return response.json();
}
