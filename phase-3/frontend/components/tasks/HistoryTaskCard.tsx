/**
 * HistoryTaskCard Component
 * Displays a deleted task in the history tab with restore functionality
 *
 * Spec: specs/002-dashboard-ux-enhancements/spec.md (FR-022, FR-026, FR-027)
 */

"use client";

import { useState } from "react";
import type { Task } from "@/types/task";
import { restoreTask } from "@/lib/task-api";

interface HistoryTaskCardProps {
  task: Task;
  onTaskRestore?: () => void;
}

export function HistoryTaskCard({ task, onTaskRestore }: HistoryTaskCardProps) {
  const [isRestoring, setIsRestoring] = useState(false);

  const handleRestore = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      setIsRestoring(true);
      await restoreTask(task.id);
      if (onTaskRestore) {
        onTaskRestore();
      }
    } catch (error) {
      console.error("Failed to restore task:", error);
    } finally {
      setIsRestoring(false);
    }
  };

  // Format deleted date
  const deletedDate = task.deleted_at
    ? new Date(task.deleted_at).toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "";

  // Get status badge color
  const getStatusColor = () => {
    switch (task.status) {
      case "completed":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300";
      case "in_progress":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300";
      case "pending":
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300";
    }
  };

  const getStatusLabel = () => {
    switch (task.status) {
      case "in_progress":
        return "In Progress";
      case "completed":
        return "Completed";
      case "pending":
      default:
        return "Pending";
    }
  };

  return (
    <div className="flex items-center gap-4 py-4 border-b border-gray-300 dark:border-gray-700 group">
      {/* Task Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <p className="text-lg text-gray-600 dark:text-gray-400">
            {task.title}
          </p>
          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusColor()}`}>
            {getStatusLabel()}
          </span>
        </div>
        {task.description && (
          <p className="text-sm text-gray-500 dark:text-gray-500 truncate">
            {task.description}
          </p>
        )}
        <p className="text-xs text-gray-400 dark:text-gray-600 mt-1">
          Deleted {deletedDate}
        </p>
      </div>

      {/* Restore Button */}
      <button
        onClick={handleRestore}
        disabled={isRestoring}
        className="flex-shrink-0 flex items-center gap-2 px-4 py-2 text-sm font-medium text-[#e08b3d] hover:text-[#d17a2f] hover:bg-orange-50 dark:hover:bg-orange-900/20 rounded-lg transition-colors disabled:opacity-50"
        title="Restore task"
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
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
        {isRestoring ? "Restoring..." : "Restore"}
      </button>
    </div>
  );
}
