"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { createTask } from "@/lib/task-api";
import type { TaskStatus } from "@/types/task";

export default function NewTaskPage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState<TaskStatus>("pending");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      setError("Title is required");
      return;
    }

    setLoading(true);
    setError("");

    try {
      await createTask({
        title: title.trim(),
        description: description.trim() || null,
        status: status,
      });

      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to create task");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8" style={{ background: '#f5f0eb' }}>
      <div className="max-w-md w-full space-y-8">
        <div>
          <Link href="/dashboard" className="text-[#e08b3d] hover:underline">
            ← Back to Dashboard
          </Link>
          <h1 className="mt-6 text-4xl font-bold text-gray-800">Create New Task</h1>
        </div>

        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                Task Title *
              </label>
              <input
                id="title"
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="w-full px-4 py-3 rounded-xl text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#e08b3d]"
                style={{ background: '#e8e2dc' }}
                placeholder="Enter task title"
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                Description (Optional)
              </label>
              <textarea
                id="description"
                rows={4}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full px-4 py-3 rounded-xl text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#e08b3d]"
                style={{ background: '#e8e2dc' }}
                placeholder="Enter task description"
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                id="status"
                value={status}
                onChange={(e) => setStatus(e.target.value as TaskStatus)}
                className="w-full px-4 py-3 rounded-xl text-gray-700 focus:outline-none focus:ring-2 focus:ring-[#e08b3d]"
                style={{ background: '#e8e2dc' }}
                disabled={loading}
              >
                <option value="pending">Pending</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>
          </div>

          <div className="flex space-x-4">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 flex justify-center py-3 px-4 text-base font-semibold rounded-xl text-white hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ background: '#e08b3d' }}
            >
              {loading ? "Creating..." : "Create Task"}
            </button>

            <Link
              href="/dashboard"
              className="flex-1 flex justify-center py-3 px-4 text-base font-semibold rounded-xl border-2 border-gray-300 text-gray-700 hover:bg-gray-50 transition-colors"
            >
              Cancel
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
