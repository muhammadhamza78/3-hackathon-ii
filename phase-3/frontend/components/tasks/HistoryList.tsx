/**
 * HistoryList Component
 * Displays list of deleted tasks with clear history functionality
 *
 * Spec: specs/002-dashboard-ux-enhancements/spec.md (FR-023, FR-024, FR-025)
 */

"use client";

import { useState } from "react";
import type { Task } from "@/types/task";
import { HistoryTaskCard } from "./HistoryTaskCard";
import { clearHistory } from "@/lib/task-api";

interface HistoryListProps {
  tasks: Task[];
  onTaskRestore?: () => void;
}

export function HistoryList({ tasks, onTaskRestore }: HistoryListProps) {
  const [showConfirm, setShowConfirm] = useState(false);
  const [isClearing, setIsClearing] = useState(false);

  const handleClearHistory = async () => {
    try {
      setIsClearing(true);
      await clearHistory();
      setShowConfirm(false);
      if (onTaskRestore) {
        onTaskRestore(); // Refresh the list
      }
    } catch (error) {
      console.error("Failed to clear history:", error);
    } finally {
      setIsClearing(false);
    }
  };

  if (tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-200 dark:bg-gray-700 rounded-full mb-4">
          <svg
            className="h-8 w-8 text-gray-400 dark:text-gray-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-700 dark:text-gray-300 mb-2">
          No history yet
        </h3>
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Deleted and cleared tasks will appear here
        </p>
      </div>
    );
  }

  return (
    <div>
      {/* Task List */}
      <div>
        {tasks.map((task) => (
          <HistoryTaskCard key={task.id} task={task} onTaskRestore={onTaskRestore} />
        ))}
      </div>

      {/* Clear History Button */}
      <div className="flex justify-end mt-6">
        {!showConfirm ? (
          <button
            onClick={() => setShowConfirm(true)}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20 rounded-lg transition-colors"
          >
            <svg
              className="h-4 w-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
              />
            </svg>
            Clear History
          </button>
        ) : (
          <div className="flex items-center gap-3 bg-red-50 dark:bg-red-900/20 px-4 py-2 rounded-lg">
            <span className="text-sm text-red-700 dark:text-red-400 font-medium">
              Permanently delete all history?
            </span>
            <button
              onClick={handleClearHistory}
              disabled={isClearing}
              className="px-3 py-1 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors disabled:opacity-50"
            >
              {isClearing ? "Deleting..." : "Yes, delete"}
            </button>
            <button
              onClick={() => setShowConfirm(false)}
              disabled={isClearing}
              className="px-3 py-1 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-md transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
