# Backend API Testing Guide

## Prerequisites

1. Start the backend server:
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

2. The server should run the database migration automatically on startup (via `init_db()` if DEBUG=True)

## Test Workflow

### 1. Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "email": "test@example.com",
  "name": null,
  "profile_picture": null,
  "created_at": "2026-01-07T10:00:00Z"
}
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

**Save the token** for subsequent requests:
```bash
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Profile Management Tests

### 3. Get Profile

```bash
curl -X GET http://localhost:8000/api/v1/profile \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "id": 1,
  "email": "test@example.com",
  "name": null,
  "profile_picture": null,
  "created_at": "2026-01-07T10:00:00Z"
}
```

### 4. Update Profile (Name)

```bash
curl -X PUT http://localhost:8000/api/v1/profile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "email": "test@example.com",
  "name": "John Doe",
  "profile_picture": null,
  "created_at": "2026-01-07T10:00:00Z"
}
```

### 5. Update Profile (Profile Picture URL)

```bash
curl -X PUT http://localhost:8000/api/v1/profile \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "profile_picture": "https://cdn.example.com/profiles/johndoe.jpg"
  }'
```

---

## Task Management Tests

### 6. Create Task

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write API docs and README",
    "status": "pending"
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "title": "Complete project documentation",
  "description": "Write API docs and README",
  "status": "pending",
  "user_id": 1,
  "created_at": "2026-01-07T10:30:00Z",
  "updated_at": "2026-01-07T10:30:00Z"
}
```

### 7. Create More Tasks (for filtering test)

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Fix login bug",
    "description": "User reports login timeout",
    "status": "in_progress"
  }'

curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Deploy to production",
    "status": "completed"
  }'
```

---

## Filter & Sort Tests

### 8. List All Tasks (No Filter)

```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Returns all active (non-deleted) tasks, sorted ascending by created_at

### 9. Filter by Status (Pending)

```bash
curl -X GET "http://localhost:8000/api/tasks?status_filter=pending" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Only pending tasks

### 10. Filter by Status (In Progress)

```bash
curl -X GET "http://localhost:8000/api/tasks?status_filter=in_progress" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Only in_progress tasks

### 11. Filter by Status (Completed)

```bash
curl -X GET "http://localhost:8000/api/tasks?status_filter=completed" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Only completed tasks

### 12. Sort Descending (Newest First)

```bash
curl -X GET "http://localhost:8000/api/tasks?sort_order=desc" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Tasks ordered by created_at DESC

### 13. Combine Filter + Sort

```bash
curl -X GET "http://localhost:8000/api/tasks?status_filter=completed&sort_order=desc" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Only completed tasks, newest first

---

## Soft Delete & History Tests

### 14. Soft Delete a Task (Move to History)

```bash
curl -X DELETE http://localhost:8000/api/tasks/1 \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** 204 No Content

### 15. Verify Task Not in Active List

```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Task ID 1 should NOT appear

### 16. Get Task History

```bash
curl -X GET http://localhost:8000/api/tasks/history \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Complete project documentation",
      "description": "Write API docs and README",
      "status": "pending",
      "user_id": 1,
      "deleted_at": "2026-01-07T10:45:00Z",
      "created_at": "2026-01-07T10:30:00Z",
      "updated_at": "2026-01-07T10:45:00Z"
    }
  ]
}
```

### 17. Restore Task from History

```bash
curl -X POST http://localhost:8000/api/tasks/1/restore \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:** Task object with deleted_at=null

### 18. Verify Task Back in Active List

```bash
curl -X GET http://localhost:8000/api/tasks \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** Task ID 1 should appear again

---

## Clear Completed Tasks Test

### 19. Mark Task as Completed

```bash
curl -X PUT http://localhost:8000/api/tasks/3 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

### 20. Clear All Completed Tasks (Move to History)

```bash
curl -X POST http://localhost:8000/api/tasks/clear-completed \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** 204 No Content

### 21. Verify Completed Tasks in History

```bash
curl -X GET http://localhost:8000/api/tasks/history \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** All cleared completed tasks appear in history

---

## Permanent Delete Test

### 22. Clear All History (Permanent Delete)

```bash
curl -X DELETE http://localhost:8000/api/tasks/history \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** 204 No Content

### 23. Verify History is Empty

```bash
curl -X GET http://localhost:8000/api/tasks/history \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "tasks": []
}
```

---

## Error Cases to Test

### Invalid Status Filter
```bash
curl -X GET "http://localhost:8000/api/tasks?status_filter=invalid" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** 400 Bad Request

### Invalid Sort Order
```bash
curl -X GET "http://localhost:8000/api/tasks?sort_order=invalid" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** 400 Bad Request

### Unauthorized Access (No Token)
```bash
curl -X GET http://localhost:8000/api/v1/profile
```

**Expected:** 401 Unauthorized

### Restore Non-existent Task
```bash
curl -X POST http://localhost:8000/api/tasks/9999/restore \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:** 404 Not Found

---

## Summary of New Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/profile` | GET | Get current user profile |
| `/api/v1/profile` | PUT | Update profile (name, picture URL) |
| `/api/tasks` | GET | List tasks with filters (?status_filter, ?sort_order) |
| `/api/tasks/{id}` | DELETE | Soft delete (move to history) |
| `/api/tasks/history` | GET | Get all deleted tasks |
| `/api/tasks/{id}/restore` | POST | Restore task from history |
| `/api/tasks/history` | DELETE | Permanently delete all history |
| `/api/tasks/clear-completed` | POST | Move completed tasks to history |

---

## Profile Picture Upload Tests (Requires Cloud Storage)

### 24. Upload Profile Picture

**Prerequisites**: Configure cloud storage (see CLOUD_STORAGE_SETUP.md)

```bash
curl -X POST http://localhost:8000/api/v1/profile/upload-picture \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/your/image.jpg"
```

**Expected Response:**
```json
{
  "id": 1,
  "email": "test@example.com",
  "name": "John Doe",
  "profile_picture": "https://your-bucket.s3.us-east-1.amazonaws.com/profiles/user-1/abc123.jpg",
  "created_at": "2026-01-07T10:00:00Z"
}
```

### 25. Upload with Invalid File Type

```bash
curl -X POST http://localhost:8000/api/v1/profile/upload-picture \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.pdf"
```

**Expected:** 400 Bad Request - "Invalid file type"

### 26. Verify Profile Picture is Publicly Accessible

```bash
curl -I https://your-bucket.s3.us-east-1.amazonaws.com/profiles/user-1/abc123.jpg
```

**Expected:** HTTP 200 OK with Content-Type: image/jpeg

---

## Complete Endpoint Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login` | POST | Login and get JWT token |
| `/api/v1/profile` | GET | Get current user profile |
| `/api/v1/profile` | PUT | Update profile (name, picture URL) |
| `/api/v1/profile/upload-picture` | POST | Upload profile picture to cloud storage |
| `/api/tasks` | POST | Create new task |
| `/api/tasks` | GET | List tasks with filters (?status_filter, ?sort_order) |
| `/api/tasks/{id}` | GET | Get single task |
| `/api/tasks/{id}` | PUT | Update task |
| `/api/tasks/{id}` | DELETE | Soft delete (move to history) |
| `/api/tasks/history` | GET | Get all deleted tasks |
| `/api/tasks/{id}/restore` | POST | Restore task from history |
| `/api/tasks/history` | DELETE | Permanently delete all history |
| `/api/tasks/clear-completed` | POST | Move completed tasks to history |

---

## Running Tests in Order

For a complete test workflow, run tests in this sequence:

1. **Auth Tests**: 1-2 (Register, Login)
2. **Profile Tests**: 3-5 (Get, Update name, Update picture URL)
3. **Task Creation**: 6-7 (Create multiple tasks)
4. **Filter/Sort**: 8-13 (Test all filter and sort combinations)
5. **Soft Delete**: 14-18 (Delete, verify history, restore)
6. **Clear Completed**: 19-21 (Mark complete, clear, verify history)
7. **Permanent Delete**: 22-23 (Clear history permanently)
8. **Upload Tests** (if cloud configured): 24-26 (Upload image)
9. **Error Cases**: Invalid inputs and unauthorized access

---

## Next Steps

1. **Configure Cloud Storage** - Follow `CLOUD_STORAGE_SETUP.md`
2. **Start Backend Server** - `uvicorn app.main:app --reload --port 8000`
3. **Run Tests** - Use the curl commands above
4. **Move to Phase 2** - Frontend implementation
