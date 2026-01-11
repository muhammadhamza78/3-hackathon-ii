/**
 * TaskList Component
 * Displays a list of tasks
 */

"use client";

import { TaskCard } from "@/components/tasks/TaskCard";
import type { Task } from "@/types/task";

interface TaskListProps {
  tasks: Task[];
  onTaskUpdate: () => void;
}

export function TaskList({ tasks, onTaskUpdate }: TaskListProps) {
  if (tasks.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No tasks found</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onTaskUpdate={onTaskUpdate}
        />
      ))}
    </div>
  );
}
