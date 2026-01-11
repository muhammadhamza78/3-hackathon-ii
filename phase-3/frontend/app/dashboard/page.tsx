"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { getTasks, getTask, clearCompletedTasks, getTaskHistory } from "@/lib/task-api";
import { TaskList } from "@/components/tasks/TaskList";
import { HistoryList } from "@/components/tasks/HistoryList";
import { FilterSort } from "@/components/tasks/FilterSort";
import { ChatContainer } from "@/components/chat";
import type { Task, TaskFilterStatus, TaskSortOrder } from "@/types/task";

type TabType = "personal" | "history";

export default function DashboardPage() {
  const [activeTab, setActiveTab] = useState<TabType>("personal");
  const [tasks, setTasks] = useState<Task[]>([]);
  const [historyTasks, setHistoryTasks] = useState<Task[]>([]);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState<TaskFilterStatus>(null);
  const [sortOrder, setSortOrder] = useState<TaskSortOrder>("asc");

  // Chat state (Phase-3)
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [userId, setUserId] = useState<number | null>(null);

  const loadTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getTasks(filterStatus, sortOrder);
      setTasks(data.tasks);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load tasks");
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    try {
      setError(null);
      const data = await getTaskHistory();
      setHistoryTasks(data.tasks);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load history");
    }
  };

  const refreshData = async () => {
    await loadTasks();
    await loadHistory();
  };

  useEffect(() => {
    refreshData();
  }, []);

  // Get user ID from JWT token (Phase-3: Chat)
  useEffect(() => {
    const token = localStorage.getItem("jwt_token");
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        setUserId(parseInt(payload.sub));
      } catch (e) {
        console.error("Failed to parse token", e);
      }
    }
  }, []);

  // Reload tasks when filter or sort changes
  useEffect(() => {
    loadTasks();
  }, [filterStatus, sortOrder]);

  // Handler for filter/sort changes
  const handleFilterChange = (status: TaskFilterStatus, sort: TaskSortOrder) => {
    setFilterStatus(status);
    setSortOrder(sort);
  };

  // Filter tasks by search query
  const filteredTasks = tasks.filter((task) =>
    task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (task.description && task.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  // Task statistics
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(t => t.status === "completed").length;
  const pendingTasks = tasks.filter(t => t.status === "pending").length;
  const inProgressTasks = tasks.filter(t => t.status === "in_progress").length;

  // Clear completed tasks
  const handleClearCompleted = async () => {
    try {
      await clearCompletedTasks();
      await refreshData(); // Refresh both tasks and history
    } catch (err) {
      console.error(err);
    }
  };

  // Handle task click to fetch full description
  const handleTaskClick = async (taskId: number) => {
    try {
      const task = await getTask(taskId);
      setSelectedTask(task);
    } catch (err) {
      console.error("Failed to fetch task", err);
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Tabs */}
      <div className="flex mb-6 border-b-2" style={{ borderColor: 'var(--card-border)' }}>
        <button
          onClick={() => setActiveTab("personal")}
          className={`px-6 py-3 text-lg font-semibold transition-colors -mb-0.5 ${
            activeTab === "personal"
              ? "border-b-4 border-[#e08b3d]"
              : "hover:opacity-70"
          }`}
          style={{ color: activeTab === "personal" ? 'var(--foreground)' : 'var(--foreground)', opacity: activeTab === "personal" ? 1 : 0.6 }}
        >
          Personal
        </button>
        <button
          onClick={() => setActiveTab("history")}
          className={`px-6 py-3 text-lg font-semibold transition-colors -mb-0.5 ${
            activeTab === "history"
              ? "border-b-4 border-[#e08b3d]"
              : "hover:opacity-70"
          }`}
          style={{ color: activeTab === "history" ? 'var(--foreground)' : 'var(--foreground)', opacity: activeTab === "history" ? 1 : 0.6 }}
        >
          History
        </button>
      </div>

      {/* Personal Tab Content */}
      {activeTab === "personal" && (
        <>
          {/* Search Bar, Filter, and Add Button */}
          <div className="mb-6">
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <svg
                  className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5"
                  style={{ color: 'var(--foreground)', opacity: 0.4 }}
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  />
                </svg>
                <input
                  type="text"
                  placeholder="Search tasks..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-12 pr-6 py-4 rounded-2xl text-lg focus:outline-none focus:ring-2 focus:ring-[#e08b3d] transition-all"
                  style={{
                    background: 'var(--input-bg)',
                    color: 'var(--input-text)'
                  }}
                />
              </div>
              <FilterSort
                onFilterChange={handleFilterChange}
                currentFilter={filterStatus}
                currentSort={sortOrder}
              />
              <Link
                href="/tasks/new"
                className="px-8 py-4 rounded-2xl text-white font-semibold text-lg hover:opacity-90 transition-opacity"
                style={{ background: '#6db9d4' }}
              >
                ADD
              </Link>
            </div>
          </div>

          {/* Task List Container */}
          <div className="rounded-3xl p-8 transition-colors" style={{ background: 'var(--accent-bg)' }}>
            {loading && (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-10 w-10 border-4 border-[#e08b3d] border-t-transparent"></div>
                <p className="mt-4 text-sm font-medium" style={{ color: 'var(--foreground)', opacity: 0.6 }}>Loading tasks...</p>
              </div>
            )}

            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 rounded-lg p-4">
                <p className="text-sm font-medium text-red-800 dark:text-red-400">{error}</p>
              </div>
            )}

            {!loading && !error && (
              <>
                <TaskList tasks={filteredTasks} onTaskUpdate={refreshData} />

                {completedTasks > 0 && (
                  <div className="flex justify-end mt-6">
                    <button
                      onClick={handleClearCompleted}
                      className="flex items-center gap-2 text-[#e08b3d] hover:text-[#d17a2f] font-medium transition-colors"
                    >
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                      </svg>
                      Clear Completed
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </>
      )}

      {/* History Tab Content */}
      {activeTab === "history" && (
        <div className="rounded-3xl p-8 transition-colors" style={{ background: 'var(--accent-bg)' }}>
          {error && (
            <div className="bg-red-50 dark:bg-red-900/20 border-l-4 border-red-500 rounded-lg p-4 mb-4">
              <p className="text-sm font-medium text-red-800 dark:text-red-400">{error}</p>
            </div>
          )}
          <HistoryList tasks={historyTasks} onTaskRestore={refreshData} />
        </div>
      )}

      {/* Selected Task Modal / Details */}
      {selectedTask && (
        <div className="mt-6 p-4 border rounded-lg shadow transition-colors" style={{
          background: 'var(--card-bg)',
          borderColor: 'var(--card-border)'
        }}>
          <h3 className="text-lg font-semibold" style={{ color: 'var(--foreground)' }}>{selectedTask.title}</h3>
          <p className="mt-2" style={{ color: 'var(--foreground)', opacity: 0.8 }}>{selectedTask.description}</p>
        </div>
      )}

      {/* Chat Button and Container (Phase-3) */}
      {userId && (
        <>
          {/* Floating Chat Button */}
          <button
            onClick={() => setIsChatOpen(!isChatOpen)}
            className={`fixed bottom-6 right-6 w-14 h-14 rounded-full shadow-lg flex items-center justify-center hover:scale-105 transition-transform z-40`}
            style={{ background: "#e08b3d" }}
            aria-label={isChatOpen ? "Close chat" : "Open chat"}
          >
            {isChatOpen ? (
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            ) : (
              <svg
                className="w-6 h-6 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                />
              </svg>
            )}
          </button>

          {/* Chat Container */}
          <ChatContainer
            userId={userId}
            isOpen={isChatOpen}
            onClose={() => setIsChatOpen(false)}
            onTaskUpdate={refreshData}
          />
        </>
      )}
    </div>
  );
}
