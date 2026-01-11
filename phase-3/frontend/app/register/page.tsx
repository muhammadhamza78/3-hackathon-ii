/**
 * Registration Page
 * User sign-up with email and password
 *
 * Spec Reference:
 * - specs/features/authentication.md (UI/UX Requirements - Registration Page)
 * - specs/ui/pages.md (Registration page)
 */

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import type { RegisterRequest, ErrorResponse } from "@/types/auth";

export default function RegisterPage() {
  const router = useRouter();
  const [formData, setFormData] = useState<RegisterRequest>({
    email: "",
    password: "",
  });
  const [name, setName] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Validate password match
    if (formData.password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    // Validate password length (client-side, server also validates)
    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters long");
      return;
    }

    if (formData.password.length > 128) {
      setError("Password must not exceed 128 characters");
      return;
    }

    setLoading(true);

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

      const response = await fetch(`${API_URL}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...formData,
          name: name.trim() || null,
        }),
      });

      if (!response.ok) {
        const errorData: ErrorResponse = await response.json();
        throw new Error(
          typeof errorData.detail === "string"
            ? errorData.detail
            : "Registration failed"
        );
      }

      // Registration successful - redirect to login with success message
      router.push("/?registered=true");
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8" style={{ background: '#f5f0eb' }}>
      <div className="max-w-md w-full space-y-8">
        {/* Header - TODO Logo */}
        <div className="text-center">
          <h1 className="text-5xl font-bold tracking-tight mb-2">
            <span className="text-gray-600">TO</span>
            <span className="text-[#e08b3d]">DO</span>
            <span className="inline-flex items-center justify-center w-12 h-12 ml-2 rounded-full bg-[#e08b3d] text-white">
              <svg className="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
              </svg>
            </span>
          </h1>
          <p className="mt-4 text-gray-600">
            Create your account
          </p>
        </div>

        {/* Registration Form */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-lg p-4" style={{ background: '#f8d7da' }}>
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div className="space-y-4">
            {/* Name Input (Optional) */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                Name (Optional)
              </label>
              <input
                id="name"
                name="name"
                type="text"
                autoComplete="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-3 rounded-xl text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#e08b3d]"
                style={{ background: '#e8e2dc' }}
                placeholder="Your name"
                maxLength={255}
              />
              <p className="mt-2 text-xs text-gray-500">
                Leave empty to use email prefix as your display name
              </p>
            </div>

            {/* Email Input */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                className="w-full px-4 py-3 rounded-xl text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#e08b3d]"
                style={{ background: '#e8e2dc' }}
                placeholder="Enter your email"
              />
            </div>

            {/* Password Input */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                minLength={8}
                maxLength={128}
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                className="w-full px-4 py-3 rounded-xl text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#e08b3d]"
                style={{ background: '#e8e2dc' }}
                placeholder="Password (min 8 characters)"
              />
              <p className="mt-2 text-xs text-gray-500">
                Must be 8-128 characters long
              </p>
            </div>

            {/* Confirm Password Input */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-xl text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#e08b3d]"
                style={{ background: '#e8e2dc' }}
                placeholder="Confirm password"
              />
            </div>
          </div>

          {/* Submit Button */}
          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-3 px-4 text-base font-semibold rounded-xl text-white hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ background: '#e08b3d' }}
            >
              {loading ? "Creating account..." : "Register"}
            </button>
          </div>

          {/* Login Link */}
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Already have an account?{" "}
              <Link
                href="/"
                className="font-medium text-[#e08b3d] hover:text-[#d17a2f]"
              >
                Login here
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}
