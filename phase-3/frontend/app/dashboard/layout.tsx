/**
 * Dashboard Layout
 * Protected layout for authenticated users with profile dropdown and theme toggle
 *
 * Spec Reference:
 * - specs/002-dashboard-ux-enhancements/spec.md (FR-005, FR-006, FR-007, FR-036)
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ProfileDropdown } from "@/components/profile/ProfileDropdown";
import { ThemeToggle } from "@/components/theme/ThemeToggle";
import { getProfile } from "@/lib/profile-api";
import type { User } from "@/types/auth";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function checkAuthAndLoadProfile() {
      // Check for JWT token
      const token = localStorage.getItem("jwt_token");
      const expiry = localStorage.getItem("token_expiry");

      if (!token || !expiry) {
        // No token - redirect to login
        router.push("/");
        return;
      }

      const expiryTime = parseInt(expiry, 10);
      if (Date.now() >= expiryTime) {
        // Token expired - clear and redirect
        localStorage.removeItem("jwt_token");
        localStorage.removeItem("token_expiry");
        localStorage.removeItem("user_email");
        router.push("/");
        return;
      }

      // Token valid - fetch user profile
      try {
        const profile = await getProfile();
        setUser(profile);
        setIsAuthenticated(true);
      } catch (error) {
        console.error("Failed to load profile:", error);
        // Token might be invalid - redirect to login
        localStorage.removeItem("jwt_token");
        localStorage.removeItem("token_expiry");
        localStorage.removeItem("user_email");
        router.push("/");
      } finally {
        setLoading(false);
      }
    }

    checkAuthAndLoadProfile();
  }, [router]);

  const handleLogout = () => {
    // Clear all auth data from localStorage
    localStorage.removeItem("jwt_token");
    localStorage.removeItem("token_expiry");
    localStorage.removeItem("user_email");
    localStorage.removeItem("user_data");

    // Redirect to login
    router.push("/login");
  };

  // Show loading state
  if (loading || !isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen transition-colors" style={{ background: 'var(--background)', color: 'var(--foreground)' }}>
      {/* Top Navigation */}
      <nav className="shadow-sm border-b transition-colors" style={{
        background: 'var(--navbar-bg)',
        borderColor: 'var(--card-border)'
      }}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            {/* Left side - Logo/Title */}
            <div className="flex items-center">
              <Link href="/dashboard" className="flex items-center space-x-1 hover:opacity-80 transition-opacity">
                <h1 className="text-4xl font-bold tracking-tight">
                  <span style={{ color: 'var(--navbar-text)', opacity: 0.6 }}>TO</span>
                  <span className="text-[#e08b3d]">DO</span>
                  <span className="inline-flex items-center justify-center w-10 h-10 ml-1 rounded-full bg-[#e08b3d] text-white">
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                  </span>
                </h1>
              </Link>
            </div>

            {/* Right side - Theme toggle and Profile */}
            <div className="flex items-center space-x-3">
              <ThemeToggle />
              <ProfileDropdown user={user} onLogout={handleLogout} />
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
}
