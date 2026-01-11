/**
 * TaskCard Component
 * Displays a single task with circular checkbox, expand arrow, and hover description.
 *
 * Spec: specs/002-dashboard-ux-enhancements/spec.md (FR-028 to FR-035)
 */

"use client";

import { useState, useRef, useEffect } from "react";
import type { Task } from "@/types/task";
import { updateTask, deleteTask } from "@/lib/task-api";

interface TaskCardProps {
  task: Task;
  onTaskUpdate?: () => void;
}

export function TaskCard({ task, onTaskUpdate }: TaskCardProps) {
  const [isUpdating, setIsUpdating] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [showDescriptionHover, setShowDescriptionHover] = useState(false);
  const cardRef = useRef<HTMLDivElement>(null);

  // Close expanded view when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (cardRef.current && !cardRef.current.contains(event.target as Node)) {
        setIsExpanded(false);
      }
    }

    if (isExpanded) {
      document.addEventListener("mousedown", handleClickOutside);
    }

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [isExpanded]);

  const handleCheckboxClick = async () => {
    try {
      setIsUpdating(true);
      const newStatus = task.status === "completed" ? "pending" : "completed";
      await updateTask(task.id, { status: newStatus });
      if (onTaskUpdate) {
        onTaskUpdate();
      }
    } catch (error) {
      console.error("Failed to update task:", error);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await deleteTask(task.id);
      if (onTaskUpdate) {
        onTaskUpdate();
      }
    } catch (error) {
      console.error("Failed to delete task:", error);
    }
  };

  const toggleExpand = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsExpanded(!isExpanded);
  };

  const isCompleted = task.status === "completed";
  const hasDescription = task.description && task.description.trim().length > 0;

  return (
    <div ref={cardRef} className="relative">
      {/* Main Task Row */}
      <div
        className="flex items-center gap-4 py-4 border-b group transition-colors"
        style={{ borderColor: 'var(--card-border)' }}
        onMouseEnter={() => hasDescription && !isExpanded && setShowDescriptionHover(true)}
        onMouseLeave={() => setShowDescriptionHover(false)}
      >
        {/* Custom Circular Checkbox */}
        <button
          onClick={handleCheckboxClick}
          disabled={isUpdating}
          className="flex-shrink-0 relative"
        >
          <div
            className={`w-7 h-7 rounded-full border-[3px] flex items-center justify-center transition-all ${
              isCompleted
                ? "bg-[#e08b3d] border-[#e08b3d]"
                : "border-gray-400 hover:border-[#e08b3d]"
            } ${isUpdating ? "opacity-50" : ""}`}
            style={{ borderColor: isCompleted ? '#e08b3d' : undefined }}
          >
            {isCompleted && (
              <svg
                className="w-5 h-5 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={3}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M5 13l4 4L19 7"
                />
              </svg>
            )}
          </div>
        </button>

        {/* Task Title */}
        <div className="flex-1 min-w-0">
          <p
            className={`text-lg ${isCompleted ? "line-through" : ""}`}
            style={{
              color: isCompleted ? 'var(--foreground)' : 'var(--foreground)',
              opacity: isCompleted ? 0.4 : 1
            }}
          >
            {task.title}
          </p>
        </div>

        {/* Hover Description Preview */}
        {showDescriptionHover && hasDescription && (
          <div className="absolute right-16 text-white text-sm px-3 py-2 rounded-lg shadow-lg max-w-xs z-10" style={{ background: '#2d2d2d' }}>
            <p className="line-clamp-2">{task.description}</p>
          </div>
        )}

        {/* Expand Arrow Button (replaces delete icon) */}
        <button
          onClick={toggleExpand}
          className={`flex-shrink-0 transition-all ${
            isExpanded
              ? "text-[#e08b3d] rotate-180"
              : "hover:text-[#e08b3d]"
          } ${hasDescription ? "opacity-100" : "opacity-0 pointer-events-none"}`}
          style={{ color: isExpanded ? '#e08b3d' : 'var(--foreground)', opacity: isExpanded ? 1 : (hasDescription ? 0.4 : 0) }}
          title={isExpanded ? "Collapse" : "Expand"}
        >
          <svg
            className="w-5 h-5 transition-transform duration-200"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M19 9l-7 7-7-7"
            />
          </svg>
        </button>
      </div>

      {/* Expanded View - Full Description + Delete */}
      {isExpanded && hasDescription && (
        <div className="px-4 py-4 border-b transition-colors" style={{
          background: 'var(--accent-bg)',
          borderColor: 'var(--card-border)'
        }}>
          <div className="flex gap-4">
            <div className="flex-1">
              <p className="text-sm whitespace-pre-wrap" style={{ color: 'var(--foreground)', opacity: 0.8 }}>
                {task.description}
              </p>
            </div>
            <button
              onClick={handleDelete}
              className="flex-shrink-0 self-start text-red-400 hover:text-red-600 dark:text-red-400 dark:hover:text-red-500 transition-colors"
              title="Delete task"
            >
              <svg
                className="w-5 h-5"
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
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
