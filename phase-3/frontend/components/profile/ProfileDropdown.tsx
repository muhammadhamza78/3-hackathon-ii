/**
 * ProfileDropdown Component
 * Displays user profile information with dropdown menu
 *
 * Spec: specs/002-dashboard-ux-enhancements/spec.md (FR-005, FR-006, FR-007)
 */

"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import type { User } from "@/types/auth";
import Avatar from "@/components/ui/Avatar";

interface ProfileDropdownProps {
  user: User | null;
  onLogout: () => void;
}

export function ProfileDropdown({ user, onLogout }: ProfileDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    if (isOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isOpen]);

  if (!user) {
    return null;
  }

  // Get display name (fallback to email if name is null)
  const displayName = user.name || user.email.split("@")[0];

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Profile Picture Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-center rounded-full border-2 hover:border-[#e08b3d] transition-all focus:outline-none focus:ring-2 focus:ring-[#e08b3d]"
        style={{ borderColor: 'var(--card-border)' }}
        aria-label="Open profile menu"
      >
        <Avatar
          name={displayName}
          profilePicture={user.profile_picture}
          size="md"
        />
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div
          className="absolute right-0 mt-2 w-64 rounded-lg shadow-lg border py-2 z-50"
          style={{
            background: 'var(--card-bg)',
            borderColor: 'var(--card-border)'
          }}
        >
          {/* Profile Picture in Dropdown */}
          <div className="px-4 py-3 border-b" style={{ borderColor: 'var(--card-border)' }}>
            <div className="flex items-center space-x-3">
              <Avatar
                name={displayName}
                profilePicture={user.profile_picture}
                size="lg"
              />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold truncate" style={{ color: 'var(--foreground)' }}>
                  {displayName}
                </p>
                <p className="text-xs truncate" style={{ color: 'var(--foreground)', opacity: 0.6 }}>
                  {user.email}
                </p>
              </div>
            </div>
          </div>

          {/* Edit Profile Button */}
          <div className="px-2 py-1">
            <button
              onClick={() => {
                setIsOpen(false);
                router.push("/dashboard/profile");
              }}
              className="w-full text-left px-3 py-2 text-sm rounded-md flex items-center space-x-2 transition-colors hover:bg-[#e08b3d] hover:bg-opacity-10"
              style={{ color: 'var(--foreground)' }}
            >
              <svg
                className="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                />
              </svg>
              <span>Edit Profile</span>
            </button>
          </div>

          {/* Logout Button */}
          <div className="px-2 py-1">
            <button
              onClick={() => {
                setIsOpen(false);
                onLogout();
              }}
              className="w-full text-left px-3 py-2 text-sm rounded-md flex items-center space-x-2 transition-colors hover:bg-[#e08b3d] hover:bg-opacity-10"
              style={{ color: 'var(--foreground)' }}
            >
              <svg
                className="w-4 h-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
              </svg>
              <span>Logout</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
