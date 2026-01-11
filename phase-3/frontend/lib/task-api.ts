/**
 * Task API Client
 * API functions for task CRUD operations with history and filters.
 *
 * Spec: specs/002-dashboard-ux-enhancements/spec.md
 */

import { apiGet, apiPost, apiPut, apiDelete } from "@/lib/api";

import type {
  Task,
  TaskCreateRequest,
  TaskUpdateRequest,
  TaskListResponse,
  TaskFilterStatus,
  TaskSortOrder,
} from "@/types/task";

/**
 * Get all active tasks for the authenticated user with optional filters.
 * Spec: FR-009 to FR-015
 */
export async function getTasks(
  statusFilter?: TaskFilterStatus,
  sortOrder?: TaskSortOrder
): Promise<TaskListResponse> {
  let url = "/api/tasks";
  const params = new URLSearchParams();

  if (statusFilter) {
    params.append("status_filter", statusFilter);
  }

  if (sortOrder) {
    params.append("sort_order", sortOrder);
  }

  if (params.toString()) {
    url += `?${params.toString()}`;
  }

  const response = await apiGet(url);

  if (!response.ok) {
    throw new Error(`Failed to fetch tasks: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get all deleted tasks (history).
 * Spec: FR-019, FR-022
 */
export async function getTaskHistory(): Promise<TaskListResponse> {
  const response = await apiGet("/api/tasks/history");

  if (!response.ok) {
    throw new Error(`Failed to fetch task history: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Create a new task.
 * Spec: FR-026 (description is optional)
 */
export async function createTask(
  data: TaskCreateRequest
): Promise<Task> {
  const response = await apiPost("/api/tasks", data);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to create task");
  }

  return response.json();
}

/**
 * Get single task.
 */
export async function getTask(id: number): Promise<Task> {
  const response = await apiGet(`/api/tasks/${id}`);

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error("Task not found");
    }
    throw new Error("Failed to fetch task");
  }

  return response.json();
}

/**
 * Update task (title, description, status).
 */
export async function updateTask(
  id: number,
  data: TaskUpdateRequest
): Promise<Task> {
  const response = await apiPut(`/api/tasks/${id}`, data);

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to update task");
  }

  return response.json();
}

/**
 * Soft delete a task (moves to history).
 * Spec: FR-021, FR-034
 */
export async function deleteTask(id: number): Promise<void> {
  const response = await apiDelete(`/api/tasks/${id}`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to delete task" }));
    throw new Error(error.detail || `Failed to delete task: ${response.statusText}`);
  }
}

/**
 * Restore a task from history back to active tasks.
 * Spec: FR-027, FR-028
 */
export async function restoreTask(id: number): Promise<Task> {
  const response = await apiPost(`/api/tasks/${id}/restore`, {});

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Failed to restore task" }));
    throw new Error(error.detail || "Failed to restore task");
  }

  return response.json();
}

/**
 * Clear all completed tasks (soft delete them - move to history).
 * Spec: FR-020
 */
export async function clearCompletedTasks(): Promise<void> {
  const response = await apiPost("/api/tasks/clear-completed", {});

  if (!response.ok) {
    throw new Error("Failed to clear completed tasks");
  }
}

/**
 * Permanently delete all tasks in history (hard delete).
 * Spec: FR-024, FR-025
 */
export async function clearHistory(): Promise<void> {
  const response = await apiDelete("/api/tasks/history");

  if (!response.ok) {
    throw new Error("Failed to clear history");
  }
}
