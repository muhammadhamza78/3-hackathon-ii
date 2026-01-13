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
1. When user asks to add/create a task, IMMEDIATELY create it - don't ask unnecessary questions
2. Extract task details from user's message (title, status, priority, deadline if mentioned)
3. If important info is missing, use smart defaults:
   - Status: "pending" (unless specified as "progress", "completed", etc)
   - Priority: "medium" (unless specified as "high" or "low")
   - Deadline: null (unless specified)
4. Respond in a concise, friendly way - NO long explanations or numbered lists
5. Always confirm what action you took

EXAMPLES:
User: "add task to read book on progress"
You: "✅ Task added: Read book (Status: In Progress)"

User: "create high priority task to finish project by tomorrow"
You: "✅ Task added: Finish project (Priority: High, Deadline: Tomorrow)"

User: "remind me to call mom"
You: "✅ Task added: Call mom"

AVAILABLE ACTIONS:
- ADD_TASK: {title, description?, status?, priority?, deadline?}
- LIST_TASKS: Show user's tasks
- UPDATE_TASK: {task_id, updates}
- DELETE_TASK: {task_id}
- COMPLETE_TASK: {task_id}

Format your response as:
ACTION: <action_name>
DATA: <json_data>
MESSAGE: <user_friendly_message>

Be direct, helpful, and don't waste user's time!"""

    def chat(self, session: Session, user_id: int, message: str, conversation_history: list) -> str:
        """
        Process user message and take direct action
        """
        # Build conversation for context
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add recent conversation history (last 5 messages)
        for msg in conversation_history[-5:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Add current user message
        messages.append({"role": "user", "content": message})
        
        # Call Groq API
        url = "https://api.groq.com/openai/v1/chat/completions"
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            ai_response = data["choices"][0]["message"]["content"]
            
            # Parse and execute action
            action_result = self._execute_action(session, user_id, ai_response, message)
            
            return action_result
            
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    def _execute_action(self, session: Session, user_id: int, ai_response: str, user_message: str) -> str:
        """
        Parse AI response and execute task actions
        """
        # Extract action from AI response
        action_match = re.search(r'ACTION:\s*(\w+)', ai_response, re.IGNORECASE)
        data_match = re.search(r'DATA:\s*({[^}]+})', ai_response, re.IGNORECASE)
        message_match = re.search(r'MESSAGE:\s*(.+?)(?:\n|$)', ai_response, re.IGNORECASE)
        
        # If AI didn't use structured format, try to detect intent
        if not action_match:
            action = self._detect_intent(user_message)
        else:
            action = action_match.group(1).upper()
        
        # Execute action
        if action == "ADD_TASK":
            return self._add_task(session, user_id, user_message, ai_response)
        elif action == "LIST_TASKS":
            return self._list_tasks(session, user_id)
        elif action == "COMPLETE_TASK":
            return self._complete_task(session, user_id, user_message)
        elif action == "DELETE_TASK":
            return self._delete_task(session, user_id, user_message)
        else:
            # Return AI's message if no specific action
            if message_match:
                return message_match.group(1).strip()
            return ai_response
    
    def _detect_intent(self, message: str) -> str:
        """
        Detect user intent from message
        """
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["add", "create", "new task", "remind"]):
            return "ADD_TASK"
        elif any(word in message_lower for word in ["list", "show", "my tasks", "what tasks"]):
            return "LIST_TASKS"
        elif any(word in message_lower for word in ["complete", "done", "finish"]):
            return "COMPLETE_TASK"
        elif any(word in message_lower for word in ["delete", "remove", "cancel"]):
            return "DELETE_TASK"
        
        return "UNKNOWN"
    
    def _add_task(self, session: Session, user_id: int, user_message: str, ai_response: str) -> str:
        """
        Add a new task directly
        """
        # Extract task details from user message
        task_title = self._extract_task_title(user_message)
        status = self._extract_status(user_message)
        priority = self._extract_priority(user_message)
        
        # Create task
        new_task = Task(
            user_id=user_id,
            title=task_title,
            description="",
            status=status,
            priority=priority,
            is_deleted=False
        )
        
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        
        # Return success message
        status_emoji = "🔄" if status == "in_progress" else "📋"
        priority_text = f" (Priority: {priority.title()})" if priority != "medium" else ""
        
        return f"✅ Task added: {task_title} {status_emoji}{priority_text}\nTask ID: #{new_task.id}"
    
    def _extract_task_title(self, message: str) -> str:
        """
        Extract task title from user message
        """
        # Remove common task-related words
        title = message.lower()
        for phrase in ["add task to", "create task to", "remind me to", "add task", "create task", "new task"]:
            title = title.replace(phrase, "")
        
        # Remove status words
        for word in ["on progress", "in progress", "high priority", "low priority", "completed", "pending"]:
            title = title.replace(word, "")
        
        # Clean up
        title = title.strip()
        
        # Capitalize first letter
        if title:
            title = title[0].upper() + title[1:]
        else:
            title = "New Task"
        
        return title
    
    def _extract_status(self, message: str) -> str:
        """
        Extract status from user message
        """
        message_lower = message.lower()
        
        if "in progress" in message_lower or "on progress" in message_lower:
            return "in_progress"
        elif "completed" in message_lower or "done" in message_lower:
            return "completed"
        else:
            return "pending"
    
    def _extract_priority(self, message: str) -> str:
        """
        Extract priority from user message
        """
        message_lower = message.lower()
        
        if "high priority" in message_lower or "urgent" in message_lower:
            return "high"
        elif "low priority" in message_lower:
            return "low"
        else:
            return "medium"
    
    def _list_tasks(self, session: Session, user_id: int) -> str:
        """
        List user's tasks
        """
        tasks = session.exec(
            select(Task).where(Task.user_id == user_id, Task.is_deleted == False)
        ).all()
        
        if not tasks:
            return "📝 You don't have any tasks yet. Add one to get started!"
        
        response = "📋 Your Tasks:\n\n"
        for task in tasks[:10]:  # Limit to 10 tasks
            status_emoji = {
                "pending": "⏳",
                "in_progress": "🔄",
                "completed": "✅"
            }.get(task.status, "📋")
            
            response += f"{status_emoji} #{task.id} - {task.title}\n"
        
        if len(tasks) > 10:
            response += f"\n...and {len(tasks) - 10} more tasks"
        
        return response
    
    def _complete_task(self, session: Session, user_id: int, message: str) -> str:
        """
        Mark task as completed
        """
        # Try to extract task ID
        task_id_match = re.search(r'#?(\d+)', message)
        if not task_id_match:
            return "Please specify which task to complete (e.g., 'complete task #5')"
        
        task_id = int(task_id_match.group(1))
        
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()
        
        if not task:
            return f"Task #{task_id} not found"
        
        task.status = "completed"
        session.commit()
        
        return f"✅ Task completed: {task.title}"
    
    def _delete_task(self, session: Session, user_id: int, message: str) -> str:
        """
        Delete a task
        """
        # Try to extract task ID
        task_id_match = re.search(r'#?(\d+)', message)
        if not task_id_match:
            return "Please specify which task to delete (e.g., 'delete task #5')"
        
        task_id = int(task_id_match.group(1))
        
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()
        
        if not task:
            return f"Task #{task_id} not found"
        
        task.is_deleted = True
        session.commit()
        
        return f"🗑️ Task deleted: {task.title}"
