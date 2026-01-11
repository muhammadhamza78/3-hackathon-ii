# TODO App - Phase 2

A modern task management application built with Next.js and FastAPI.

## Features

- ✅ User authentication with JWT
- ✅ Task CRUD operations
- ✅ Task history with soft delete
- ✅ Profile management with optional username and avatar
- ✅ Dark/Light theme toggle
- ✅ Filter and sort tasks by status
- ✅ Responsive design

## Project Structure

```
phase-2/
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/     # API endpoints
│   │   ├── auth/    # Authentication
│   │   ├── db/      # Database config
│   │   ├── models/  # SQLModel models
│   │   └── schemas/ # Pydantic schemas
│   └── requirements.txt
├── frontend/         # Next.js frontend
│   ├── app/         # App router pages
│   ├── components/  # React components
│   ├── lib/         # Utilities
│   └── types/       # TypeScript types
└── README.md
```

## Tech Stack

**Backend:**
- FastAPI
- SQLModel (PostgreSQL)
- Pydantic v2
- JWT authentication
- Python 3.11+

**Frontend:**
- Next.js 15
- TypeScript
- Tailwind CSS
- React Hooks

## Getting Started

### Backend Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database URL and JWT secret
```

3. Run the server:
```bash
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
# Edit with your API URL
```

3. Run the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

## API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Features in Detail

### Authentication
- Email/password registration and login
- Optional username (auto-generated from email if not provided)
- JWT token-based authentication
- Profile picture support (URL-based)

### Task Management
- Create, read, update, delete tasks
- Task status: pending, in_progress, completed
- Soft delete (move to history)
- Restore from history
- Clear completed tasks
- Clear all history

### UI/UX
- Dark and light theme with smooth transitions
- Colorful avatars with first letter display
- Profile edit page
- Filter and sort tasks
- Responsive design for all screen sizes

## License

MIT
