"use client";

import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import Avatar from "@/components/ui/Avatar";
import { getProfile, updateProfile } from "@/lib/profile-api";
import type { User } from "@/types/auth";

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [name, setName] = useState("");
  const [profilePictureUrl, setProfilePictureUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    loadProfile();
  }, []);

  async function loadProfile() {
    try {
      const profile = await getProfile();
      setUser(profile);
      setName(profile.name || "");
      setProfilePictureUrl(profile.profile_picture || "");
    } catch (err) {
      console.error("Failed to load profile:", err);
      setError("Failed to load profile");
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setSuccess("");
    setIsLoading(true);

    try {
      const updatedUser = await updateProfile({
        name: name.trim() || null,
        profile_picture: profilePictureUrl.trim() || null,
      });

      // Update local storage
      if (typeof window !== "undefined") {
        localStorage.setItem("user_data", JSON.stringify(updatedUser));
      }

      setUser(updatedUser);
      setSuccess("Profile updated successfully!");

      // Refresh the page after 1 second
      setTimeout(() => {
        window.location.reload();
      }, 1000);
    } catch (err: any) {
      setError(err.message || "Failed to update profile");
    } finally {
      setIsLoading(false);
    }
  }

  function handleImageSelect() {
    fileInputRef.current?.click();
  }

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    // For now, just show a message about image upload
    // In production, you'd upload to cloud storage (S3, Cloudinary, etc.)
    setError("Image upload to cloud storage not yet implemented. Please use a direct URL for now.");
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center" style={{ color: 'var(--foreground)', opacity: 0.6 }}>
          Loading profile...
        </div>
      </div>
    );
  }

  const displayName = user.name || user.email.split("@")[0];

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-6">
        <button
          onClick={() => router.push("/dashboard")}
          className="flex items-center gap-2 text-sm transition-colors hover:text-[#e08b3d]"
          style={{ color: 'var(--foreground)', opacity: 0.8 }}
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
          Back to Dashboard
        </button>
      </div>

      <div className="rounded-3xl p-8 transition-colors" style={{ background: 'var(--card-bg)' }}>
        <h1 className="text-3xl font-bold mb-6" style={{ color: 'var(--foreground)' }}>
          Edit Profile
        </h1>

        {/* Profile Picture Section */}
        <div className="flex items-center gap-6 mb-8 pb-8 border-b" style={{ borderColor: 'var(--card-border)' }}>
          <Avatar
            name={displayName}
            profilePicture={user.profile_picture}
            size="lg"
          />
          <div className="flex-1">
            <p className="text-lg font-semibold mb-1" style={{ color: 'var(--foreground)' }}>
              Profile Picture
            </p>
            <p className="text-sm mb-3" style={{ color: 'var(--foreground)', opacity: 0.6 }}>
              {user.profile_picture ? "Change your profile picture" : "Upload a profile picture or enter a URL"}
            </p>
            <div className="flex gap-2">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
              />
              <button
                onClick={handleImageSelect}
                className="px-4 py-2 rounded-lg text-sm font-medium border transition-colors"
                style={{
                  background: 'var(--card-bg)',
                  color: 'var(--foreground)',
                  borderColor: 'var(--card-border)',
                }}
              >
                Upload Image
              </button>
            </div>
          </div>
        </div>

        {/* Error/Success Messages */}
        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-500 bg-opacity-10 border border-red-500 text-red-500 text-sm">
            {error}
          </div>
        )}
        {success && (
          <div className="mb-4 p-3 rounded-lg bg-green-500 bg-opacity-10 border border-green-500 text-green-500 text-sm">
            {success}
          </div>
        )}

        {/* Profile Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Name Field */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium mb-2" style={{ color: 'var(--foreground)' }}>
              Display Name
            </label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={user.email.split("@")[0]}
              className="w-full px-4 py-3 rounded-lg text-base border transition-colors"
              style={{
                background: 'var(--input-bg)',
                color: 'var(--input-text)',
                borderColor: 'var(--card-border)',
              }}
              maxLength={255}
            />
            <p className="mt-1 text-xs" style={{ color: 'var(--foreground)', opacity: 0.6 }}>
              Leave empty to use email prefix ({user.email.split("@")[0]})
            </p>
          </div>

          {/* Profile Picture URL */}
          <div>
            <label htmlFor="profilePicture" className="block text-sm font-medium mb-2" style={{ color: 'var(--foreground)' }}>
              Profile Picture URL (Optional)
            </label>
            <input
              id="profilePicture"
              type="url"
              value={profilePictureUrl}
              onChange={(e) => setProfilePictureUrl(e.target.value)}
              placeholder="https://example.com/your-photo.jpg"
              className="w-full px-4 py-3 rounded-lg text-base border transition-colors"
              style={{
                background: 'var(--input-bg)',
                color: 'var(--input-text)',
                borderColor: 'var(--card-border)',
              }}
              maxLength={500}
            />
            <p className="mt-1 text-xs" style={{ color: 'var(--foreground)', opacity: 0.6 }}>
              Enter a direct image URL. Leave empty to show first letter.
            </p>
          </div>

          {/* Email (Read-only) */}
          <div>
            <label htmlFor="email" className="block text-sm font-medium mb-2" style={{ color: 'var(--foreground)' }}>
              Email
            </label>
            <input
              id="email"
              type="email"
              value={user.email}
              disabled
              className="w-full px-4 py-3 rounded-lg text-base border transition-colors cursor-not-allowed"
              style={{
                background: 'var(--input-bg)',
                color: 'var(--input-text)',
                borderColor: 'var(--card-border)',
                opacity: 0.6,
              }}
            />
            <p className="mt-1 text-xs" style={{ color: 'var(--foreground)', opacity: 0.6 }}>
              Email cannot be changed
            </p>
          </div>

          {/* Submit Button */}
          <div className="flex gap-3 pt-4">
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 bg-[#e08b3d] hover:bg-[#d17a2f] text-white font-semibold py-3 px-6 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? "Saving..." : "Save Changes"}
            </button>
            <button
              type="button"
              onClick={() => router.push("/dashboard")}
              className="px-6 py-3 rounded-lg font-semibold border transition-colors"
              style={{
                background: 'var(--card-bg)',
                color: 'var(--foreground)',
                borderColor: 'var(--card-border)',
              }}
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
