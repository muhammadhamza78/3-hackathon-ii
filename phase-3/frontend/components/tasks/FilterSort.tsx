/**
 * FilterSort Component
 * Provides filtering and sorting options for the task list
 *
 * Spec: specs/002-dashboard-ux-enhancements/spec.md (FR-009 to FR-015)
 */

"use client";

import { useState, useRef, useEffect } from "react";
import type { TaskFilterStatus, TaskSortOrder } from "@/types/task";

interface FilterSortProps {
  onFilterChange: (status: TaskFilterStatus, sortOrder: TaskSortOrder) => void;
  currentFilter: TaskFilterStatus;
  currentSort: TaskSortOrder;
}

export function FilterSort({ onFilterChange, currentFilter, currentSort }: FilterSortProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState<TaskFilterStatus>(currentFilter);
  const [selectedSort, setSelectedSort] = useState<TaskSortOrder>(currentSort);
  const dropdownRef = useRef<HTMLDivElement>(null);

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

  const handleApply = () => {
    onFilterChange(selectedStatus, selectedSort);
    setIsOpen(false);
  };

  const handleClear = () => {
    setSelectedStatus(null);
    setSelectedSort("asc");
    onFilterChange(null, "asc");
    setIsOpen(false);
  };

  // Check if any filters are active
  const hasActiveFilters = currentFilter !== null || currentSort !== "asc";

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Filter Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all border"
        style={{
          background: hasActiveFilters ? '#e08b3d' : 'var(--card-bg)',
          color: hasActiveFilters ? 'white' : 'var(--foreground)',
          borderColor: hasActiveFilters ? '#e08b3d' : 'var(--card-border)'
        }}
        title="Filter and sort tasks"
      >
        <svg
          className="h-5 w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"
          />
        </svg>
        Filter
        {hasActiveFilters && (
          <span className="inline-flex items-center justify-center w-5 h-5 text-xs bg-white text-[#e08b3d] rounded-full">
            !
          </span>
        )}
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-72 rounded-lg shadow-lg border z-50 transition-colors" style={{
          background: 'var(--card-bg)',
          borderColor: 'var(--card-border)'
        }}>
          <div className="p-4">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold" style={{ color: 'var(--foreground)' }}>
                Filter & Sort
              </h3>
              <button
                onClick={() => setIsOpen(false)}
                className="hover:opacity-70 transition-opacity"
                style={{ color: 'var(--foreground)', opacity: 0.6 }}
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Status Filter Section */}
            <div className="mb-5">
              <h4 className="text-sm font-medium mb-3" style={{ color: 'var(--foreground)', opacity: 0.8 }}>
                Status
              </h4>
              <div className="space-y-2">
                {[
                  { value: null, label: "All Tasks" },
                  { value: "pending", label: "Pending" },
                  { value: "in_progress", label: "In Progress" },
                  { value: "completed", label: "Completed" }
                ].map((option) => (
                  <label key={String(option.value)} className="flex items-center cursor-pointer group">
                    <input
                      type="radio"
                      name="status"
                      checked={selectedStatus === option.value}
                      onChange={() => setSelectedStatus(option.value as any)}
                      className="w-4 h-4 text-[#e08b3d] focus:ring-[#e08b3d] focus:ring-2"
                    />
                    <span className="ml-3 text-sm group-hover:opacity-100 transition-opacity" style={{ color: 'var(--foreground)', opacity: 0.8 }}>
                      {option.label}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Sort Section */}
            <div className="mb-5">
              <h4 className="text-sm font-medium mb-3" style={{ color: 'var(--foreground)', opacity: 0.8 }}>
                Sort By Date
              </h4>
              <div className="space-y-2">
                {[
                  { value: "asc", label: "Oldest First" },
                  { value: "desc", label: "Newest First" }
                ].map((option) => (
                  <label key={option.value} className="flex items-center cursor-pointer group">
                    <input
                      type="radio"
                      name="sort"
                      checked={selectedSort === option.value}
                      onChange={() => setSelectedSort(option.value as any)}
                      className="w-4 h-4 text-[#e08b3d] focus:ring-[#e08b3d] focus:ring-2"
                    />
                    <span className="ml-3 text-sm group-hover:opacity-100 transition-opacity" style={{ color: 'var(--foreground)', opacity: 0.8 }}>
                      {option.label}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-2 pt-3 border-t transition-colors" style={{ borderColor: 'var(--card-border)' }}>
              <button
                onClick={handleClear}
                className="flex-1 px-4 py-2 text-sm font-medium rounded-lg transition-all hover:opacity-80"
                style={{
                  color: 'var(--foreground)',
                  background: 'var(--accent-bg)'
                }}
              >
                Clear
              </button>
              <button
                onClick={handleApply}
                className="flex-1 px-4 py-2 text-sm font-medium text-white bg-[#e08b3d] hover:bg-[#d17a2f] rounded-lg transition-colors"
              >
                Apply
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
