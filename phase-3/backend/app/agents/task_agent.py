# import os
# import requests
# import re
# from sqlmodel import Session, select
# from app.models.task import Task
# from datetime import datetime


# class TaskAgent:
#     def __init__(self):
#         self.api_key = os.environ.get("GROQ_API_KEY")
#         if not self.api_key:
#             raise ValueError("GROQ_API_KEY not set")
        
#         self.system_prompt = """You are a direct, action-oriented task management assistant. 

# RULES:
# 1. When user asks to add/create a task, IMMEDIATELY create it - don't ask unnecessary questions
# 2. Extract task details from user's message (title, status, priority, deadline if mentioned)
# 3. If important info is missing, use smart defaults:
#    - Status: "pending" (unless specified as "progress", "completed", etc)
#    - Priority: "medium" (unless specified as "high" or "low")
#    - Deadline: null (unless specified)
# 4. Respond in a concise, friendly way - NO long explanations or numbered lists
# 5. Always confirm what action you took

# EXAMPLES:
# User: "add task to read book on progress"
# You: "✅ Task added: Read book (Status: In Progress)"

# User: "create high priority task to finish project by tomorrow"
# You: "✅ Task added: Finish project (Priority: High, Deadline: Tomorrow)"

# User: "remind me to call mom"
# You: "✅ Task added: Call mom"

# AVAILABLE ACTIONS:
# - ADD_TASK: {title, description?, status?, priority?, deadline?}
# - LIST_TASKS: Show user's tasks
# - UPDATE_TASK: {task_id, updates}
# - DELETE_TASK: {task_id}
# - COMPLETE_TASK: {task_id}

# Format your response as:
# ACTION: <action_name>
# DATA: <json_data>
# MESSAGE: <user_friendly_message>

# Be direct, helpful, and don't waste user's time!"""

#     def chat(self, session: Session, user_id: int, message: str, conversation_history: list) -> str:
#         """
#         Process user message and take direct action
#         """
#         # Build conversation for context
#         messages = [{"role": "system", "content": self.system_prompt}]
        
#         # Add recent conversation history (last 5 messages)
#         for msg in conversation_history[-5:]:
#             messages.append({
#                 "role": msg.get("role", "user"),
#                 "content": msg.get("content", "")
#             })
        
#         # Add current user message
#         messages.append({"role": "user", "content": message})
        
#         # Call Groq API
#         url = "https://api.groq.com/openai/v1/chat/completions"
#         payload = {
#             "model": "llama-3.3-70b-versatile",
#             "messages": messages,
#             "temperature": 0.7,
#             "max_tokens": 500
#         }
#         headers = {
#             "Authorization": f"Bearer {self.api_key}",
#             "Content-Type": "application/json"
#         }
        
#         try:
#             resp = requests.post(url, json=payload, headers=headers, timeout=30)
#             resp.raise_for_status()
#             data = resp.json()
#             ai_response = data["choices"][0]["message"]["content"]
            
#             # Parse and execute action
#             action_result = self._execute_action(session, user_id, ai_response, message)
            
#             return action_result
            
#         except Exception as e:
#             return f"Sorry, I encountered an error: {str(e)}"
    
#     def _execute_action(self, session: Session, user_id: int, ai_response: str, user_message: str) -> str:
#         """
#         Parse AI response and execute task actions
#         """
#         # Extract action from AI response
#         action_match = re.search(r'ACTION:\s*(\w+)', ai_response, re.IGNORECASE)
#         data_match = re.search(r'DATA:\s*({[^}]+})', ai_response, re.IGNORECASE)
#         message_match = re.search(r'MESSAGE:\s*(.+?)(?:\n|$)', ai_response, re.IGNORECASE)
        
#         # If AI didn't use structured format, try to detect intent
#         if not action_match:
#             action = self._detect_intent(user_message)
#         else:
#             action = action_match.group(1).upper()
        
#         # Execute action
#         if action == "ADD_TASK":
#             return self._add_task(session, user_id, user_message, ai_response)
#         elif action == "LIST_TASKS":
#             return self._list_tasks(session, user_id)
#         elif action == "COMPLETE_TASK":
#             return self._complete_task(session, user_id, user_message)
#         elif action == "DELETE_TASK":
#             return self._delete_task(session, user_id, user_message)
#         else:
#             # Return AI's message if no specific action
#             if message_match:
#                 return message_match.group(1).strip()
#             return ai_response
    
#     def _detect_intent(self, message: str) -> str:
#         """
#         Detect user intent from message
#         """
#         message_lower = message.lower()
        
#         if any(word in message_lower for word in ["add", "create", "new task", "remind"]):
#             return "ADD_TASK"
#         elif any(word in message_lower for word in ["list", "show", "my tasks", "what tasks"]):
#             return "LIST_TASKS"
#         elif any(word in message_lower for word in ["complete", "done", "finish"]):
#             return "COMPLETE_TASK"
#         elif any(word in message_lower for word in ["delete", "remove", "cancel"]):
#             return "DELETE_TASK"
        
#         return "UNKNOWN"
    
#     def _add_task(self, session: Session, user_id: int, user_message: str, ai_response: str) -> str:
#         """
#         Add a new task directly
#         """
#         # Extract task details from user message
#         task_title = self._extract_task_title(user_message)
#         status = self._extract_status(user_message)
#         priority = self._extract_priority(user_message)
        
#         # Create task
#         new_task = Task(
#             user_id=user_id,
#             title=task_title,
#             description="",
#             status=status,
#             priority=priority,
#             is_deleted=False
#         )
        
#         session.add(new_task)
#         session.commit()
#         session.refresh(new_task)
        
#         # Return success message
#         status_emoji = "🔄" if status == "in_progress" else "📋"
#         priority_text = f" (Priority: {priority.title()})" if priority != "medium" else ""
        
#         return f"✅ Task added: {task_title} {status_emoji}{priority_text}\nTask ID: #{new_task.id}"
    
#     def _extract_task_title(self, message: str) -> str:
#         """
#         Extract task title from user message
#         """
#         # Remove common task-related words
#         title = message.lower()
#         for phrase in ["add task to", "create task to", "remind me to", "add task", "create task", "new task"]:
#             title = title.replace(phrase, "")
        
#         # Remove status words
#         for word in ["on progress", "in progress", "high priority", "low priority", "completed", "pending"]:
#             title = title.replace(word, "")
        
#         # Clean up
#         title = title.strip()
        
#         # Capitalize first letter
#         if title:
#             title = title[0].upper() + title[1:]
#         else:
#             title = "New Task"
        
#         return title
    
#     def _extract_status(self, message: str) -> str:
#         """
#         Extract status from user message
#         """
#         message_lower = message.lower()
        
#         if "in progress" in message_lower or "on progress" in message_lower:
#             return "in_progress"
#         elif "completed" in message_lower or "done" in message_lower:
#             return "completed"
#         else:
#             return "pending"
    
#     def _extract_priority(self, message: str) -> str:
#         """
#         Extract priority from user message
#         """
#         message_lower = message.lower()
        
#         if "high priority" in message_lower or "urgent" in message_lower:
#             return "high"
#         elif "low priority" in message_lower:
#             return "low"
#         else:
#             return "medium"
    
#     def _list_tasks(self, session: Session, user_id: int) -> str:
#         """
#         List user's tasks
#         """
#         tasks = session.exec(
#             select(Task).where(Task.user_id == user_id, Task.is_deleted == False)
#         ).all()
        
#         if not tasks:
#             return "📝 You don't have any tasks yet. Add one to get started!"
        
#         response = "📋 Your Tasks:\n\n"
#         for task in tasks[:10]:  # Limit to 10 tasks
#             status_emoji = {
#                 "pending": "⏳",
#                 "in_progress": "🔄",
#                 "completed": "✅"
#             }.get(task.status, "📋")
            
#             response += f"{status_emoji} #{task.id} - {task.title}\n"
        
#         if len(tasks) > 10:
#             response += f"\n...and {len(tasks) - 10} more tasks"
        
#         return response
    
#     def _complete_task(self, session: Session, user_id: int, message: str) -> str:
#         """
#         Mark task as completed
#         """
#         # Try to extract task ID
#         task_id_match = re.search(r'#?(\d+)', message)
#         if not task_id_match:
#             return "Please specify which task to complete (e.g., 'complete task #5')"
        
#         task_id = int(task_id_match.group(1))
        
#         task = session.exec(
#             select(Task).where(Task.id == task_id, Task.user_id == user_id)
#         ).first()
        
#         if not task:
#             return f"Task #{task_id} not found"
        
#         task.status = "completed"
#         session.commit()
        
#         return f"✅ Task completed: {task.title}"
    
#     def _delete_task(self, session: Session, user_id: int, message: str) -> str:
#         """
#         Delete a task
#         """
#         # Try to extract task ID
#         task_id_match = re.search(r'#?(\d+)', message)
#         if not task_id_match:
#             return "Please specify which task to delete (e.g., 'delete task #5')"
        
#         task_id = int(task_id_match.group(1))
        
#         task = session.exec(
#             select(Task).where(Task.id == task_id, Task.user_id == user_id)
#         ).first()
        
#         if not task:
#             return f"Task #{task_id} not found"
        
#         task.is_deleted = True
#         session.commit()
        
#         return f"🗑️ Task deleted: {task.title}"












import os
import requests
import re
from sqlmodel import Session, select
from app.models.task import Task
from datetime import datetime


class TaskAgent:
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set")
        
        self.system_prompt = """You are a direct, action-oriented task management assistant. 

RULES:
1. When user asks to add/create a task → IMMEDIATELY create it
2. When user asks to edit/update a task → IMMEDIATELY update it
3. When user asks to delete/remove a task → IMMEDIATELY delete it
4. When user asks to complete/mark done a task → IMMEDIATELY mark it complete
5. Extract details from user's message - don't ask unnecessary questions
6. Respond concisely - NO long explanations

EXAMPLES:

User: "add task to read book"
Action: ADD_TASK
Response: "✅ Task added: Read book"

User: "edit task read book to learn python"
Action: UPDATE_TASK
Response: "✅ Task updated: Learn python"

User: "delete task read book"
Action: DELETE_TASK
Response: "🗑️ Task deleted: Read book"

User: "complete task read book"
Action: COMPLETE_TASK
Response: "✅ Task completed: Read book"

User: "show my tasks"
Action: LIST_TASKS
Response: Show tasks list

DETECT INTENT from keywords:
- add, create, new, remind → ADD
- edit, update, change, modify, rename → UPDATE
- delete, remove, cancel → DELETE
- complete, done, finish, mark done → COMPLETE
- show, list, my tasks → LIST

Always include the task title/ID in your response so I can identify which task to act on."""

    def chat(self, session: Session, user_id: int, message: str, conversation_history: list) -> str:
        """Process user message and take direct action"""
        
        print(f"\n{'='*60}")
        print(f"🤖 TaskAgent Processing")
        print(f"   User: {user_id}")
        print(f"   Message: {message}")
        print(f"{'='*60}\n")
        
        # Detect intent directly from message
        intent = self._detect_intent(message)
        print(f"🎯 Detected Intent: {intent}")
        
        # Execute action based on intent
        if intent == "ADD":
            return self._add_task(session, user_id, message)
        elif intent == "EDIT":
            return self._edit_task(session, user_id, message)
        elif intent == "DELETE":
            return self._delete_task(session, user_id, message)
        elif intent == "COMPLETE":
            return self._complete_task(session, user_id, message)
        elif intent == "LIST":
            return self._list_tasks(session, user_id)
        else:
            # For general chat, use AI
            return self._general_chat(message, conversation_history)
    
    def _detect_intent(self, message: str) -> str:
        """Detect user intent from message keywords"""
        msg = message.lower()
        
        # Check for edit/update first (more specific)
        if any(word in msg for word in ["edit", "update", "change", "modify", "rename"]):
            return "EDIT"
        
        # Check for delete
        if any(word in msg for word in ["delete", "remove", "cancel"]):
            return "DELETE"
        
        # Check for complete
        if any(word in msg for word in ["complete", "done", "finish", "mark done", "mark as done"]):
            return "COMPLETE"
        
        # Check for list
        if any(word in msg for word in ["list", "show", "my tasks", "what tasks", "all tasks"]):
            return "LIST"
        
        # Check for add (should be last as it's most generic)
        if any(word in msg for word in ["add", "create", "new", "remind"]):
            return "ADD"
        
        return "CHAT"
    
    def _add_task(self, session: Session, user_id: int, message: str) -> str:
        """Add a new task"""
        print("➕ Adding task...")
        
        # Extract task details
        title = self._extract_task_title(message, action="add")
        status = self._extract_status(message)
        priority = self._extract_priority(message)
        
        # Create task
        new_task = Task(
            user_id=user_id,
            title=title,
            description="",
            status=status,
            priority=priority,
            is_deleted=False
        )
        
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        
        print(f"✅ Task created: {title} (ID: {new_task.id})")
        
        # Status emoji
        status_emoji = "🔄" if status == "in_progress" else "📋"
        priority_text = f" (Priority: {priority.title()})" if priority != "medium" else ""
        
        return f"✅ Task added: {title} {status_emoji}{priority_text}"
    
    def _edit_task(self, session: Session, user_id: int, message: str) -> str:
        """Edit an existing task"""
        print("✏️ Editing task...")
        
        # Try to find which task to edit
        # Pattern: "edit [old_title] to [new_title]"
        
        # First, get all user's tasks
        tasks = session.exec(
            select(Task).where(Task.user_id == user_id, Task.is_deleted == False)
        ).all()
        
        if not tasks:
            return "❌ No tasks found to edit"
        
        # Extract old and new titles
        msg = message.lower()
        
        # Try pattern: "edit X to Y"
        edit_patterns = [
            r'edit\s+(?:task\s+)?(.+?)\s+to\s+(.+)',
            r'update\s+(?:task\s+)?(.+?)\s+to\s+(.+)',
            r'change\s+(?:task\s+)?(.+?)\s+to\s+(.+)',
            r'rename\s+(?:task\s+)?(.+?)\s+to\s+(.+)',
        ]
        
        old_title = None
        new_title = None
        
        for pattern in edit_patterns:
            match = re.search(pattern, msg, re.IGNORECASE)
            if match:
                old_title = match.group(1).strip()
                new_title = match.group(2).strip()
                break
        
        if not old_title or not new_title:
            return "❌ Please specify: 'edit [old task name] to [new task name]'"
        
        # Find matching task (fuzzy match)
        matching_task = None
        for task in tasks:
            if old_title in task.title.lower() or task.title.lower() in old_title:
                matching_task = task
                break
        
        if not matching_task:
            return f"❌ Task '{old_title}' not found. Use 'show my tasks' to see all tasks."
        
        # Update task title
        old_task_title = matching_task.title
        matching_task.title = new_title.capitalize()
        
        session.commit()
        
        print(f"✅ Task updated: {old_task_title} → {new_title}")
        
        return f"✅ Task updated: {new_title}"
    
    def _delete_task(self, session: Session, user_id: int, message: str) -> str:
        """Delete a task"""
        print("🗑️ Deleting task...")
        
        # Get all tasks
        tasks = session.exec(
            select(Task).where(Task.user_id == user_id, Task.is_deleted == False)
        ).all()
        
        if not tasks:
            return "❌ No tasks found to delete"
        
        # Extract task title to delete
        msg = message.lower()
        
        # Remove delete keywords
        title_to_delete = msg
        for word in ["delete", "remove", "cancel", "task"]:
            title_to_delete = title_to_delete.replace(word, "")
        title_to_delete = title_to_delete.strip()
        
        if not title_to_delete:
            return "❌ Please specify which task to delete (e.g., 'delete read book')"
        
        # Find matching task
        matching_task = None
        for task in tasks:
            if title_to_delete in task.title.lower() or task.title.lower() in title_to_delete:
                matching_task = task
                break
        
        if not matching_task:
            return f"❌ Task '{title_to_delete}' not found"
        
        # Soft delete
        task_title = matching_task.title
        matching_task.is_deleted = True
        session.commit()
        
        print(f"✅ Task deleted: {task_title}")
        
        return f"🗑️ Task deleted: {task_title}"
    
    def _complete_task(self, session: Session, user_id: int, message: str) -> str:
        """Mark task as completed"""
        print("✅ Completing task...")
        
        # Get all tasks
        tasks = session.exec(
            select(Task).where(Task.user_id == user_id, Task.is_deleted == False)
        ).all()
        
        if not tasks:
            return "❌ No tasks found to complete"
        
        # Extract task title
        msg = message.lower()
        
        # Remove complete keywords
        title_to_complete = msg
        for word in ["complete", "done", "finish", "mark", "as", "task"]:
            title_to_complete = title_to_complete.replace(word, "")
        title_to_complete = title_to_complete.strip()
        
        if not title_to_complete:
            return "❌ Please specify which task to complete (e.g., 'complete read book')"
        
        # Find matching task
        matching_task = None
        for task in tasks:
            if title_to_complete in task.title.lower() or task.title.lower() in title_to_complete:
                matching_task = task
                break
        
        if not matching_task:
            return f"❌ Task '{title_to_complete}' not found"
        
        # Mark as completed
        task_title = matching_task.title
        matching_task.status = "completed"
        session.commit()
        
        print(f"✅ Task completed: {task_title}")
        
        return f"✅ Task completed: {task_title}"
    
    def _list_tasks(self, session: Session, user_id: int) -> str:
        """List all tasks"""
        print("📋 Listing tasks...")
        
        tasks = session.exec(
            select(Task).where(Task.user_id == user_id, Task.is_deleted == False)
        ).all()
        
        if not tasks:
            return "📝 You don't have any tasks yet. Add one to get started!"
        
        response = "📋 Your Tasks:\n\n"
        for task in tasks[:10]:
            status_emoji = {
                "pending": "⏳",
                "in_progress": "🔄",
                "completed": "✅"
            }.get(task.status, "📋")
            
            response += f"{status_emoji} {task.title}\n"
        
        if len(tasks) > 10:
            response += f"\n...and {len(tasks) - 10} more tasks"
        
        return response
    
    def _general_chat(self, message: str, conversation_history: list) -> str:
        """Handle general chat with AI"""
        print("💬 General chat...")
        
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add history
        for msg in conversation_history[-5:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        messages.append({"role": "user", "content": message})
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 300
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    def _extract_task_title(self, message: str, action: str = "add") -> str:
        """Extract task title from message"""
        title = message.lower()
        
        # Remove action keywords
        if action == "add":
            for phrase in ["add task to", "create task to", "remind me to", "add task", "create task", "new task", "add"]:
                title = title.replace(phrase, "")
        
        # Remove status/priority words
        for word in ["on progress", "in progress", "high priority", "low priority", "completed", "pending"]:
            title = title.replace(word, "")
        
        # Clean up
        title = title.strip()
        
        # Capitalize
        if title:
            title = title[0].upper() + title[1:]
        else:
            title = "New Task"
        
        return title
    
    def _extract_status(self, message: str) -> str:
        """Extract status from message"""
        msg = message.lower()
        
        if "in progress" in msg or "on progress" in msg:
            return "in_progress"
        elif "completed" in msg or "done" in msg:
            return "completed"
        else:
            return "pending"
    
    def _extract_priority(self, message: str) -> str:
        """Extract priority from message"""
        msg = message.lower()
        
        if "high priority" in msg or "urgent" in msg:
            return "high"
        elif "low priority" in msg:
            return "low"
        else:
            return "medium"
