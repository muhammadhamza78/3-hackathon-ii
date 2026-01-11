/**
 * Login Page (Landing Page)
 * User authentication with email and password
 *
 * Spec Reference:
 * - specs/features/authentication.md (UI/UX Requirements - Login Page)
 * - specs/ui/pages.md (Landing / Login page)
 */

"use client";

import { useState, useEffect, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import type { LoginRequest, ErrorResponse } from "@/types/auth";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [formData, setFormData] = useState<LoginRequest>({
    email: "",
    password: "",
  });
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");

  useEffect(() => {
    // Check if user just registered
    if (searchParams.get("registered") === "true") {
      setSuccessMessage("Account created successfully! Please log in.");
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData: ErrorResponse = await response.json();
        throw new Error(
          typeof errorData.detail === "string"
            ? errorData.detail
            : "Login failed"
        );
      }

      const data = await response.json();

      // Store JWT token and expiry
      localStorage.setItem("jwt_token", data.access_token);
      localStorage.setItem("token_expiry", (Date.now() + data.expires_in * 1000).toString());
      localStorage.setItem("user_email", formData.email);

      // Store user data from response
      if (data.user) {
        localStorage.setItem("user_data", JSON.stringify({
          id: data.user.id,
          email: data.user.email,
          name: data.user.name,
          profile_picture: data.user.profile_picture
        }));
      }

      // Redirect to dashboard
      router.push("/dashboard");
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
            Sign in to your account
          </p>
        </div>

        {/* Login Form */}
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {successMessage && (
            <div className="rounded-lg p-4" style={{ background: '#d4edda' }}>
              <p className="text-sm text-green-800">{successMessage}</p>
            </div>
          )}

          {error && (
            <div className="rounded-lg p-4" style={{ background: '#f8d7da' }}>
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div className="space-y-4">
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
                autoComplete="current-password"
                required
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                className="w-full px-4 py-3 rounded-xl text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#e08b3d]"
                style={{ background: '#e8e2dc' }}
                placeholder="Enter your password"
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
              {loading ? "Signing in..." : "Sign in"}
            </button>
          </div>

          {/* Register Link */}
          <div className="text-center">
            <p className="text-sm text-gray-600">
              Don't have an account?{" "}
              <Link
                href="/register"
                className="font-medium text-[#e08b3d] hover:text-[#d17a2f]"
              >
                Register here
              </Link>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
      <LoginForm />
    </Suspense>
  );
}
