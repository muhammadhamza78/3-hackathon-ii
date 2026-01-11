"""
Task Agent
Groq-powered agent for natural language task management.

Spec Reference: specs/phase-3-chatbot-spec.md (FR-011 to FR-018)
"""

from groq import Groq
from sqlmodel import Session
from typing import Optional, List, Dict, Any
import json
import re

from app.mcp.tools import add_task, list_tasks, complete_task, update_task, delete_task
from app.config import settings


# Simplified system prompt without complex function calling
SYSTEM_PROMPT = """You are a helpful task management assistant. You help users manage their todo tasks.

When the user asks you to perform task operations, respond in a structured format:

For ADD TASK:
ACTION: ADD_TASK
TITLE: [task title]
DESCRIPTION: [optional description]
STATUS: [pending/in_progress/completed]

For LIST TASKS:
ACTION: LIST_TASKS
FILTER: [all/pending/in_progress/completed]

For COMPLETE TASK:
ACTION: COMPLETE_TASK
TASK: [task title or ID]

For UPDATE TASK:
ACTION: UPDATE_TASK
TASK: [task title or ID]
TITLE: [new title if changing]
DESCRIPTION: [new description if changing]
STATUS: [new status if changing]

For DELETE TASK:
ACTION: DELETE_TASK
TASK: [task title or ID]

Examples:
User: "add a task to buy groceries"
Assistant: 
ACTION: ADD_TASK
TITLE: buy groceries
STATUS: pending

User: "show me all my tasks"
Assistant:
ACTION: LIST_TASKS
FILTER: all

User: "mark groceries as done"
Assistant:
ACTION: COMPLETE_TASK
TASK: groceries

Always include a friendly confirmation message after the action format."""


class TaskAgent:
    """
    AI Agent for natural language task management.
    Uses Groq with structured output parsing (no function calling).
    """

    def __init__(self):
        """Initialize the Groq client."""
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL or "llama-3.3-70b-versatile"

    def _parse_action(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse structured action from AI response."""
        lines = response_text.strip().split('\n')
        action = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('ACTION:'):
                action['type'] = line.split(':', 1)[1].strip()
            elif line.startswith('TITLE:'):
                action['title'] = line.split(':', 1)[1].strip()
            elif line.startswith('DESCRIPTION:'):
                action['description'] = line.split(':', 1)[1].strip()
            elif line.startswith('STATUS:'):
                action['status'] = line.split(':', 1)[1].strip()
            elif line.startswith('FILTER:'):
                action['filter'] = line.split(':', 1)[1].strip()
            elif line.startswith('TASK:'):
                action['task'] = line.split(':', 1)[1].strip()
        
        return action if 'type' in action else None

    def _execute_action(
        self,
        session: Session,
        user_id: int,
        action: Dict[str, Any]
    ) -> str:
        """Execute parsed action and return result."""
        action_type = action.get('type', '').upper()
        
        try:
            if action_type == 'ADD_TASK':
                result = add_task(
                    session=session,
                    user_id=user_id,
                    title=action.get('title', ''),
                    description=action.get('description'),
                    status=action.get('status', 'pending')
                )
                return json.dumps(result.model_dump())
            
            elif action_type == 'LIST_TASKS':
                result = list_tasks(
                    session=session,
                    user_id=user_id,
                    status_filter=action.get('filter', 'all')
                )
                return json.dumps(result.model_dump())
            
            elif action_type == 'COMPLETE_TASK':
                result = complete_task(
                    session=session,
                    user_id=user_id,
                    task_identifier=action.get('task', '')
                )
                return json.dumps(result.model_dump())
            
            elif action_type == 'UPDATE_TASK':
                result = update_task(
                    session=session,
                    user_id=user_id,
                    task_identifier=action.get('task', ''),
                    title=action.get('title'),
                    description=action.get('description'),
                    status=action.get('status')
                )
                return json.dumps(result.model_dump())
            
            elif action_type == 'DELETE_TASK':
                result = delete_task(
                    session=session,
                    user_id=user_id,
                    task_identifier=action.get('task', '')
                )
                return json.dumps(result.model_dump())
            
            else:
                return json.dumps({
                    "success": False,
                    "message": "Unknown action type"
                })
        
        except Exception as e:
            return json.dumps({
                "success": False,
                "message": f"Error: {str(e)}"
            })

    def chat(
        self,
        session: Session,
        user_id: int,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Process a chat message and return the response.

        Args:
            session: Database session
            user_id: User making the request
            message: User's message
            conversation_history: Previous messages for context

        Returns:
            Assistant's response string
        """
        # Build messages array
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add conversation history (limited to last N messages)
        if conversation_history:
            context_limit = settings.CHAT_CONTEXT_MESSAGES or 20
            messages.extend(conversation_history[-context_limit:])

        # Add current message
        messages.append({"role": "user", "content": message})

        try:
            # Call Groq (no function calling, just text)
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1024,
                temperature=0.7
            )

            response_text = response.choices[0].message.content or ""
            
            # Try to parse action from response
            action = self._parse_action(response_text)
            
            if action:
                # Execute the action
                result_json = self._execute_action(session, user_id, action)
                result = json.loads(result_json)
                
                # Generate friendly response with result
                result_message = f"\n\nResult: {json.dumps(result, indent=2)}"
                
                # Ask AI to format the response nicely
                messages.append({"role": "assistant", "content": response_text})
                messages.append({"role": "user", "content": f"The action completed with this result: {result_json}. Please give me a friendly summary."})
                
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=512,
                    temperature=0.7
                )
                
                return final_response.choices[0].message.content or "Done!"
            
            # No action detected, return direct response
            return response_text

        except Exception as e:
            return f"I encountered an error processing your request. Please try again. (Error: {str(e)})"
        
        
        
        
        
        
        
        
        
        

# """
# Task Agent
# Groq-powered agent for natural language task management.

# Spec Reference: specs/phase-3-chatbot-spec.md (FR-011 to FR-018)
# """

# from groq import Groq
# from sqlmodel import Session
# from typing import Optional, List, Dict, Any
# import json

# from app.mcp.tools import add_task, list_tasks, complete_task, update_task, delete_task
# from app.config import settings


# # Groq Tool Definitions (OpenAI-compatible format)
# TOOLS = [
#     {
#         "type": "function",
#         "function": {
#             "name": "add_task",
#             "description": "Create a new task. Use this when the user wants to add, create, or make a new task.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "title": {
#                         "type": "string",
#                         "description": "The title/name of the task"
#                     },
#                     "description": {
#                         "type": "string",
#                         "description": "Optional detailed description of the task"
#                     },
#                     "status": {
#                         "type": "string",
#                         "enum": ["pending", "in_progress", "completed"],
#                         "description": "Initial status. Default is 'pending'. Use 'in_progress' if user says 'in progress' or 'started'."
#                     }
#                 },
#                 "required": ["title"]
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "list_tasks",
#             "description": "List all tasks. Use when user asks to see, show, list, or view their tasks.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "status_filter": {
#                         "type": "string",
#                         "enum": ["all", "pending", "in_progress", "completed"],
#                         "description": "Filter by status. Use 'all' to show everything."
#                     }
#                 }
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "complete_task",
#             "description": "Mark a task as completed. Use when user says they finished, completed, or done with a task.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "task_identifier": {
#                         "type": "string",
#                         "description": "The task title or ID to mark as complete"
#                     }
#                 },
#                 "required": ["task_identifier"]
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "update_task",
#             "description": "Update a task's title, description, or status. Use when user wants to change, edit, modify, or update a task.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "task_identifier": {
#                         "type": "string",
#                         "description": "The task title or ID to update"
#                     },
#                     "title": {
#                         "type": "string",
#                         "description": "New title for the task"
#                     },
#                     "description": {
#                         "type": "string",
#                         "description": "New description for the task"
#                     },
#                     "status": {
#                         "type": "string",
#                         "enum": ["pending", "in_progress", "completed"],
#                         "description": "New status for the task"
#                     }
#                 },
#                 "required": ["task_identifier"]
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "delete_task",
#             "description": "Delete a task (moves to history). Use when user wants to delete, remove, or trash a task.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "task_identifier": {
#                         "type": "string",
#                         "description": "The task title or ID to delete"
#                     }
#                 },
#                 "required": ["task_identifier"]
#             }
#         }
#     }
# ]


# SYSTEM_PROMPT = """You are a helpful task management assistant. You help users manage their todo tasks through natural language conversation.

# Your capabilities:
# - Add new tasks (with title, optional description, and status)
# - List tasks (all or filtered by status: pending, in_progress, completed)
# - Mark tasks as complete
# - Update task details (title, description, status)
# - Delete tasks (soft delete - they go to history and can be restored)

# IMPORTANT: When parsing "add task" or "delete task" commands in this format:
# "add task Title: X description: Y status: Z"
# "delete task Title: X description: Y status: Z"
# - Extract the title after "Title:" (this is the task identifier)
# - Extract the description after "description:" (optional)
# - Extract the status after "status:" (convert "in progress" to "in_progress")

# For example:
# "add task Title: Read book description: Daily 10 pages status: in progress"
# Should create: title="Read book", description="Daily 10 pages", status="in_progress"

# "delete task Title: Read book description: Daily 10 pages status: in progress"
# Should delete the task with title "Read book"

# Also handle natural formats like:
# - "add a task to buy groceries" -> title="buy groceries"
# - "create task: call mom" -> title="call mom"
# - "remind me to exercise" -> title="exercise"
# - "delete the grocery task" -> delete task with "grocery" in title
# - "remove read book" -> delete task with "read book" in title

# When referencing existing tasks, try to match by title. If multiple tasks match, ask for clarification.

# Always confirm actions taken with a brief, friendly response.
# Keep responses concise but helpful."""


# class TaskAgent:
#     """
#     AI Agent for natural language task management.
#     Uses Groq (FREE) with function calling to execute MCP tools.
#     """

#     def __init__(self):
#         """Initialize the Groq client."""
#         self.client = Groq(api_key=settings.GROQ_API_KEY)
#         self.model = settings.GROQ_MODEL or "llama-3.3-70b-versatile"

#     def _execute_tool(
#         self,
#         session: Session,
#         user_id: int,
#         tool_name: str,
#         arguments: Dict[str, Any]
#     ) -> str:
#         """
#         Execute an MCP tool and return JSON result.

#         Args:
#             session: Database session
#             user_id: User making the request
#             tool_name: Name of the tool to execute
#             arguments: Tool arguments

#         Returns:
#             JSON string with tool result
#         """
#         tool_map = {
#             "add_task": add_task,
#             "list_tasks": list_tasks,
#             "complete_task": complete_task,
#             "update_task": update_task,
#             "delete_task": delete_task
#         }

#         tool_func = tool_map.get(tool_name)
#         if not tool_func:
#             return json.dumps({
#                 "success": False,
#                 "message": f"Unknown tool: {tool_name}"
#             })

#         try:
#             result = tool_func(session, user_id, **arguments)
#             return json.dumps(result.model_dump())
#         except Exception as e:
#             return json.dumps({
#                 "success": False,
#                 "message": f"Tool execution error: {str(e)}"
#             })

#     def chat(
#         self,
#         session: Session,
#         user_id: int,
#         message: str,
#         conversation_history: Optional[List[Dict[str, str]]] = None
#     ) -> str:
#         """
#         Process a chat message and return the response.

#         Args:
#             session: Database session
#             user_id: User making the request
#             message: User's message
#             conversation_history: Previous messages for context

#         Returns:
#             Assistant's response string
#         """
#         # Build messages array
#         messages = [{"role": "system", "content": SYSTEM_PROMPT}]

#         # Add conversation history (limited to last N messages)
#         if conversation_history:
#             context_limit = settings.CHAT_CONTEXT_MESSAGES or 20
#             messages.extend(conversation_history[-context_limit:])

#         # Add current message
#         messages.append({"role": "user", "content": message})

#         try:
#             # Call Groq with tools (OpenAI-compatible API)
#             response = self.client.chat.completions.create(
#                 model=self.model,
#                 messages=messages,
#                 tools=TOOLS,
#                 tool_choice="auto",
#                 max_tokens=1024,
#                 temperature=0.7
#             )

#             assistant_message = response.choices[0].message

#             # Handle tool calls if present
#             if assistant_message.tool_calls:
#                 # Add assistant's message with tool calls
#                 messages.append({
#                     "role": "assistant",
#                     "content": assistant_message.content or "",
#                     "tool_calls": [
#                         {
#                             "id": tc.id,
#                             "type": "function",
#                             "function": {
#                                 "name": tc.function.name,
#                                 "arguments": tc.function.arguments
#                             }
#                         }
#                         for tc in assistant_message.tool_calls
#                     ]
#                 })

#                 # Execute each tool and collect results
#                 for tool_call in assistant_message.tool_calls:
#                     tool_name = tool_call.function.name
#                     arguments = json.loads(tool_call.function.arguments)

#                     result = self._execute_tool(
#                         session, user_id, tool_name, arguments
#                     )

#                     messages.append({
#                         "role": "tool",
#                         "tool_call_id": tool_call.id,
#                         "content": result
#                     })

#                 # Get final response after tool execution
#                 final_response = self.client.chat.completions.create(
#                     model=self.model,
#                     messages=messages,
#                     max_tokens=1024,
#                     temperature=0.7
#                 )

#                 return final_response.choices[0].message.content or "Done!"

#             # No tool calls, return direct response
#             return assistant_message.content or "I'm not sure how to help with that. Try asking me to add, list, complete, update, or delete tasks."

#         except Exception as e:
#             return f"I encountered an error processing your request. Please try again. (Error: {str(e)})"