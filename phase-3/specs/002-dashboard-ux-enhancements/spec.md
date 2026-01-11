# Feature Specification: Todo App UI/UX Improvements

**Feature Branch**: `002-dashboard-ux-enhancements`
**Created**: 2026-01-07
**Status**: Draft
**Input**: User description: "Todo App UI/UX Improvements: Profile section with picture upload, user name, dropdown menu. Theme toggle. History tab for deleted/completed tasks. Filters (status, sorting). Task description on hover/expand with new delete interaction. Responsive design."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Profile Management in Navbar (Priority: P1)

Users need a personalized profile section in the navbar to manage their account information and access logout functionality, replacing the current simple email display.

**Why this priority**: This is the most visible change affecting every page view. It establishes user identity throughout the app and provides essential account management capabilities. Without this, users have a subpar authentication experience.

**Independent Test**: Can be fully tested by logging in, clicking the profile section in the navbar, viewing profile information (name, email, picture), uploading a profile picture, and logging out. Delivers immediate value by improving user identity representation.

**Acceptance Scenarios**:

1. **Given** user is logged in, **When** user views the navbar, **Then** the TODO logo appears on the left and profile picture appears on the right (replacing the email text and logout button)
2. **Given** user clicks on the profile picture/section, **When** dropdown opens, **Then** user sees profile picture, user name, user email, and logout button
3. **Given** user has not uploaded a profile picture, **When** viewing profile section, **Then** a default profile image is displayed
4. **Given** user clicks to upload profile picture, **When** user selects an image file, **Then** profile picture updates immediately throughout the app
5. **Given** user clicks logout in profile dropdown, **When** logout completes, **Then** user is redirected to login page and session is cleared

---

### User Story 2 - Task Filtering and Sorting (Priority: P2)

Users need to filter and sort their tasks by status and order to quickly find and organize their work, especially as task lists grow longer.

**Why this priority**: As users accumulate tasks, finding specific items becomes difficult. Filtering by status (pending, in-progress, completed) and sorting capabilities are essential productivity features. This builds on the existing task display without requiring new infrastructure.

**Independent Test**: Can be fully tested by creating multiple tasks with different statuses, clicking the filter icon, applying status filters (show only pending, in-progress, or completed), applying sort order (ascending/descending), and clearing filters to return to default view. Delivers value by improving task discoverability.

**Acceptance Scenarios**:

1. **Given** user is on Personal tasks view, **When** user views the section header, **Then** a filter icon appears on the right side
2. **Given** user clicks filter icon, **When** filter menu opens, **Then** user sees options: Status filters (In-progress, Pending, Completed), Sorting (Ascending, Descending), and Clear Filter
3. **Given** user selects "Pending" status filter, **When** filter is applied, **Then** only pending tasks are displayed in the list
4. **Given** user selects "In-progress" status filter, **When** filter is applied, **Then** only in-progress tasks are displayed
5. **Given** user selects "Completed" status filter, **When** filter is applied, **Then** only completed tasks are displayed
6. **Given** user selects Ascending sort, **When** sort is applied, **Then** tasks appear in top-to-bottom order (oldest to newest by creation date)
7. **Given** user selects Descending sort, **When** sort is applied, **Then** tasks appear in bottom-to-top order (newest to oldest by creation date)
8. **Given** user has active filters, **When** user clicks "Clear Filter", **Then** all tasks display in default line-wise order with no filters applied

---

### User Story 3 - Task History Tab (Priority: P3)

Users need to view deleted and cleared completed tasks in a separate History section, allowing them to review past work and permanently remove items when ready.

**Why this priority**: Users often accidentally delete tasks or want to reference completed work. A history feature provides a safety net and audit trail. This is a new capability requiring database schema changes for soft deletes.

**Independent Test**: Can be fully tested by completing and clearing tasks, deleting tasks, switching to the History tab to view them, and using the clear history button for permanent deletion. Delivers value by providing task recovery and historical tracking.

**Acceptance Scenarios**:

1. **Given** user is on dashboard, **When** user views the section tabs, **Then** user sees "Personal" tab (currently selected) and "History" tab
2. **Given** user has cleared completed tasks from Personal, **When** user clicks History tab, **Then** cleared completed tasks appear in the history list
3. **Given** user has deleted a task from Personal, **When** user views History tab, **Then** deleted task appears in the history list
4. **Given** user is viewing History tab, **When** user views a task entry, **Then** task shows its title, status, and timestamp of deletion/completion
5. **Given** user clicks "Clear History" button, **When** confirmation is accepted, **Then** all history tasks are permanently deleted from the database
6. **Given** a task is in History, **When** user clicks restore button on the task, **Then** task is moved back to Personal tab as an active task (soft delete reversed)

---

### User Story 4 - Enhanced Task Description Display (Priority: P4)

Users need better access to task descriptions with improved interaction patterns, replacing the current delete icon with an expandable view that shows both description and delete options.

**Why this priority**: Task descriptions provide context but are currently hidden. This enhancement makes descriptions more accessible while maintaining a clean default view. It refines an existing feature with better UX patterns.

**Independent Test**: Can be fully tested by creating tasks with and without descriptions, hovering over tasks to see descriptions, clicking the downward arrow to expand full details and access delete, and verifying the interaction works consistently across all tasks.

**Acceptance Scenarios**:

1. **Given** user is creating a new task, **When** viewing the task form, **Then** description field is optional (can be left blank)
2. **Given** task has a description, **When** user hovers over the task in Personal section, **Then** description text appears on the right side of the task row
3. **Given** task has no description, **When** user hovers over the task, **Then** no description text appears (or shows "No description")
4. **Given** user views a task row, **When** looking at the right side, **Then** a downward arrow icon appears (replacing the current dustbin delete icon)
5. **Given** user clicks the downward arrow, **When** task expands, **Then** full description is displayed below the task title along with delete option
6. **Given** task is expanded, **When** user clicks delete option, **Then** task is moved to History (soft delete)
7. **Given** task has no description, **When** user clicks the downward arrow, **Then** expanded view shows "No description" message and delete option

---

### User Story 5 - Light/Dark Theme Toggle (Priority: P5)

Users need to switch between light and dark themes to match their preference and reduce eye strain in different lighting conditions.

**Why this priority**: Theme customization improves accessibility and user comfort. While valuable, it's a cosmetic enhancement that doesn't affect core functionality. Can be implemented after core features are stable.

**Independent Test**: Can be fully tested by clicking the theme toggle button near the profile section, observing the entire app switch between light and dark color schemes, and verifying the preference persists across sessions.

**Acceptance Scenarios**:

1. **Given** user is on dashboard, **When** user views the navbar near profile section, **Then** a theme toggle button (sun/moon icon) is visible
2. **Given** app is in light theme, **When** user clicks theme toggle, **Then** entire app switches to dark theme with appropriate color palette
3. **Given** app is in dark theme, **When** user clicks theme toggle, **Then** entire app switches to light theme
4. **Given** user has selected a theme, **When** user logs out and logs back in, **Then** selected theme preference is preserved
5. **Given** user changes theme, **When** viewing all UI elements (navbar, tasks, buttons, forms), **Then** all elements display with appropriate contrast and readability in the selected theme

---

### Edge Cases

- **Profile Picture Upload**: What happens when user uploads an invalid file type or file size exceeds limit (e.g., 5MB)? System should validate format (JPEG, PNG, GIF) and size, showing clear error message.
- **Empty History**: What happens when user views History tab with no deleted/completed tasks? Display empty state message: "No history yet. Deleted and cleared tasks will appear here."
- **Filter with No Matching Tasks**: What happens when status filter is applied but no tasks match? Display empty state: "No [status] tasks found. Clear filter to see all tasks."
- **Concurrent Theme Changes**: How does system handle theme preference if user has multiple browser tabs open? Use localStorage and broadcast channel to sync theme across tabs in real-time.
- **Long Task Descriptions**: What happens when task description exceeds display area on hover? Truncate with ellipsis on hover preview, show full text in expanded view with scrolling if needed.
- **Profile Name Missing**: What happens when user profile doesn't have a name set? Display email address as fallback name in profile dropdown.
- **Network Failure on Profile Picture Upload**: What happens if upload fails due to network error? Show retry button and preserve old profile picture until successful upload.

## Requirements *(mandatory)*

### Functional Requirements

#### Profile & Authentication (P1)

- **FR-001**: System MUST store user profile information including name and profile picture URL in the users table
- **FR-002**: System MUST provide an API endpoint to update user profile (name, profile picture)
- **FR-003**: System MUST support profile picture upload with file validation (format: JPEG/PNG/GIF, max size: 5MB)
- **FR-004**: System MUST serve a default profile picture when user has not uploaded a custom image
- **FR-005**: Navbar MUST display profile picture on the right side (replacing current email display)
- **FR-006**: Clicking profile picture MUST open a dropdown menu showing profile picture, user name, user email, and logout button
- **FR-007**: Logout button MUST only appear in profile dropdown (removed from main navbar)
- **FR-008**: TODO logo/text MUST remain on left side of navbar in current position

#### Task Filtering & Sorting (P2)

- **FR-009**: Personal tasks section header MUST display a filter icon on the right side
- **FR-010**: Clicking filter icon MUST open a filter menu with options: Status (In-progress, Pending, Completed), Sorting (Ascending, Descending), Clear Filter
- **FR-011**: Selecting a status filter MUST display only tasks matching that status
- **FR-012**: Ascending sort MUST display tasks in top-to-bottom order by creation timestamp
- **FR-013**: Descending sort MUST display tasks in bottom-to-top order by creation timestamp
- **FR-014**: Clear Filter option MUST reset view to show all tasks in default order
- **FR-015**: Filter state MUST persist during the user session but reset on page reload

#### Task History (P3)

- **FR-016**: System MUST implement soft delete for tasks (add deleted_at timestamp field to tasks table)
- **FR-017**: Dashboard MUST display two tabs: "Personal" (default) and "History"
- **FR-018**: Personal tab MUST show only active tasks (deleted_at is null)
- **FR-019**: History tab MUST show tasks where deleted_at is not null OR tasks that were cleared as completed
- **FR-020**: Clearing completed tasks from Personal MUST mark them as deleted (set deleted_at timestamp)
- **FR-021**: Deleting a task MUST perform soft delete (set deleted_at, keep in database)
- **FR-022**: History tab MUST display task title, status, and deletion/completion timestamp
- **FR-023**: History tab MUST include "Clear History" button
- **FR-024**: Clear History action MUST permanently delete (hard delete) all history tasks from database
- **FR-025**: Clear History MUST require user confirmation before permanent deletion
- **FR-026**: Each task in History MUST display a restore button or action
- **FR-027**: Clicking restore on a history task MUST clear deleted_at timestamp (set to null) and move task back to Personal tab
- **FR-028**: Restored tasks MUST retain their original title, description, status, and creation timestamp

#### Task Description Display (P4)

- **FR-029**: Task creation form MUST make description field optional (can be blank)
- **FR-030**: Task row in Personal section MUST display description on right side when user hovers over task (if description exists)
- **FR-031**: Task row MUST display downward arrow icon instead of dustbin delete icon
- **FR-032**: Clicking downward arrow MUST expand task to show full description and delete option
- **FR-033**: Expanded task view MUST display "No description" message if task has no description
- **FR-034**: Delete option in expanded view MUST perform soft delete (move to History)
- **FR-035**: Clicking outside expanded task MUST collapse it back to default view

#### Theme Management (P5)

- **FR-036**: Navbar MUST display theme toggle button (sun/moon icon) near profile section
- **FR-037**: Theme toggle MUST switch entire application between light and dark color schemes
- **FR-038**: Dark theme MUST use appropriate dark background colors, light text, and adjusted accent colors
- **FR-039**: Light theme MUST use current color scheme (default)
- **FR-040**: Theme preference MUST be stored in localStorage
- **FR-041**: Theme preference MUST persist across browser sessions for the same user
- **FR-042**: All UI components (navbar, tasks, buttons, forms, modals) MUST render correctly in both themes with proper contrast

#### Cross-Cutting Requirements

- **FR-043**: All new features MUST be fully responsive for desktop (1024px+) and mobile (320px+) viewports
- **FR-044**: All interactive elements (profile dropdown, filters, theme toggle, task expansion) MUST include hover states and smooth transitions
- **FR-045**: Profile picture upload MUST show loading state during upload and error message on failure
- **FR-046**: All API endpoints MUST require authentication and validate user ownership of resources

### Key Entities

- **User**: Represents authenticated user account
  - Attributes: id, email, hashed_password, name (new), profile_picture_url (new), theme_preference (new), created_at, updated_at
  - Relationships: owns many Tasks

- **Task**: Represents a todo item owned by a user
  - Attributes: id, title, description (optional), status (pending/in_progress/completed), user_id, deleted_at (new), created_at, updated_at
  - Relationships: belongs to one User
  - Soft Delete: deleted_at timestamp indicates task is in history; null means active

- **ProfilePicture**: Metadata for uploaded profile images
  - Attributes: filename, url, file_size, mime_type, uploaded_at
  - Storage: Cloud storage (AWS S3, Cloudflare R2, or similar) with CDN for scalable image delivery

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can access profile information and logout within 2 clicks from any page (click profile picture, then logout)
- **SC-002**: Users can filter task list by status and see filtered results in under 1 second
- **SC-003**: Users can view task descriptions without navigating away from the task list (hover or expand in place)
- **SC-004**: Users can recover accidentally deleted tasks from History tab before permanent deletion
- **SC-005**: Profile picture upload completes and displays within 3 seconds for images up to 5MB on standard broadband
- **SC-006**: Theme toggle switches entire app appearance instantly (under 300ms perceived delay)
- **SC-007**: All features render correctly on mobile devices (320px width) and desktop (1920px width) without horizontal scrolling
- **SC-008**: 95% of users successfully complete profile setup (name + picture) on first attempt without errors
- **SC-009**: Filter functionality reduces time to find specific task status by 70% compared to manual scanning
- **SC-010**: History feature reduces accidental permanent task loss by 100% (all deletes are recoverable until history is cleared)

## Assumptions

- Users have modern browsers supporting CSS custom properties (for theming), localStorage, and File API
- Profile pictures will be public-facing (no sensitive content) and don't require additional privacy controls
- Task history retention is indefinite until user manually clears it (no automatic expiration)
- Default sort order for tasks is creation date ascending (oldest first)
- Email address is always available and can be used as fallback when user name is not set
- Mobile breakpoint is 768px, tablet is 768-1023px, desktop is 1024px+
- Maximum of 1000 tasks in history before performance optimization is needed (pagination/virtualization)
- Theme preference is browser-specific (not synced across devices) unless user logs in

## Dependencies

- Frontend: React/Next.js framework for UI components and state management
- Backend: Existing FastAPI user authentication and task CRUD endpoints
- Database: Existing SQLModel schema (will require migrations for new fields)
- File Storage: Solution needed for profile picture uploads (local/cloud)

## Out of Scope

- Social features (sharing tasks, collaborative lists)
- Task restore functionality from History (one-way move to history)
- Advanced filtering (by date range, keywords, tags)
- Profile customization beyond name and picture (bio, preferences, settings page)
- Theme customization (only light/dark toggle, no custom color schemes)
- Bulk task operations (select multiple, bulk delete, bulk status change)
- Task history export or archiving
- Profile picture editing tools (crop, rotate, filters)
- Animation preferences or motion controls
- Keyboard shortcuts for filter/theme operations
