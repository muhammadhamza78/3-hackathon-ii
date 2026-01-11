/**
 * Task Type Definitions
 * TypeScript interfaces for task CRUD operations.
 *
 * Spec Reference: specs/features/task-crud.md (Task Data Model)
 * Plan Reference: specs/features/plans/data-model.md (TypeScript Types)
 */

/**
 * Task status enum matching backend TaskStatus.
 *
 * Values:
 * - pending: Task not yet started (default)
 * - in_progress: Task currently being worked on
 * - completed: Task finished
 *
 * Research: specs/features/plans/research.md (R1: Enum Implementation)
 */
export type TaskStatus = "pending" | "in_progress" | "completed";

/**
 * Task model representing a user's todo item.
 *
 * All fields match backend TaskResponse schema exactly.
 *
 * Spec: specs/features/task-crud.md (Task Data Model)
 */
export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: TaskStatus;
  user_id: number;
  deleted_at: string | null; // ISO 8601 datetime string - null for active tasks
  created_at: string; // ISO 8601 datetime string
  updated_at: string; // ISO 8601 datetime string
}

/**
 * Filter and sort options for task list
 */
export type TaskFilterStatus = "pending" | "in_progress" | "completed" | null;
export type TaskSortOrder = "asc" | "desc";

/**
 * Request payload for creating a new task.
 *
 * Spec: specs/features/task-crud.md (FR1: Create Task)
 * Contract: specs/features/plans/contracts/task-create.json
 */
export interface TaskCreateRequest {
  title: string;
  description?: string | null;
  status?: TaskStatus;
}

/**
 * Request payload for updating an existing task.
 * All fields are optional (partial update).
 *
 * Spec: specs/features/task-crud.md (FR4: Update Task)
 * Contract: specs/features/plans/contracts/task-update.json
 */
export interface TaskUpdateRequest {
  title?: string;
  description?: string | null;
  status?: TaskStatus;
}

/**
 * Response payload for task list endpoint.
 *
 * Spec: specs/features/task-crud.md (FR2: List All Tasks)
 * Contract: specs/features/plans/contracts/task-list.json
 */
export interface TaskListResponse {
  tasks: Task[];
}

/**
 * Error response from API.
 * Matches FastAPI Pydantic validation error structure.
 *
 * Research: specs/features/plans/research.md (R6: Error Handling)
 */
export interface TaskErrorResponse {
  detail: string | ValidationError[];
}

export interface ValidationError {
  loc: string[];
  msg: string;
  type: string;
}
