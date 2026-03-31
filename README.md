# 🐾 PawPal+ - Smart Pet Care Scheduler

**PawPal+** is an intelligent Streamlit application that helps busy pet owners plan and manage daily care tasks for their pets. Using smart scheduling algorithms, conflict detection, and recurring task automation, PawPal+ makes pet care planning simple and efficient.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## ✨ Key Features

### Core Functionality
- **Multi-Pet Management** — Manage tasks for multiple pets in one interface
- **Task Management** — Create, edit, and organize pet care tasks with priority levels
- **Priority-Based Scheduling** — Automatically sort tasks by importance (HIGH → MEDIUM → LOW)
- **Time Preferences** — Organize tasks by time of day (morning, afternoon, evening, flexible)
- **Daily Schedule Generation** — Get a complete daily plan optimized by priority and time constraints

### Smart Algorithms
- **Intelligent Sorting** — Sort tasks by time of day or priority with a single click
- **Advanced Filtering** — Filter tasks by completion status or priority level
- **Conflict Detection** — Automatic warnings when multiple tasks are scheduled at the same time
- **Recurring Task Automation** — Daily and weekly tasks automatically create next occurrences
- **Time Validation** — Ensures your schedule fits within available time

### User Experience
- **Streamlit Web Interface** — Clean, intuitive web-based interface
- **Real-Time Updates** — Changes persist across page refreshes using session state
- **Professional Metrics** — View statistics on task completion, time allocation, and conflicts
- **Interactive Filtering & Sorting** — Customize your view with advanced controls

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smart Scheduling Features

PawPal+ includes intelligent algorithms that make scheduling smarter:

### Sorting & Filtering
- **Sort by Time of Day** — Organize tasks by morning, afternoon, or evening preferences
- **Sort by Priority** — Rank tasks by importance (HIGH → MEDIUM → LOW)
- **Filter by Status** — View only completed or pending tasks
- **Filter by Priority** — Focus on high-priority tasks for the day

### Recurring Tasks
- **Daily Tasks** — Automatically create tomorrow's instance when marked complete
- **Weekly Tasks** — Create next week's instance with Python's `timedelta`
- **One-time Tasks** — Tasks that don't recur

### Conflict Detection
- **Automatic Warnings** — Detects when multiple tasks are scheduled for the same time
- **Conservative Approach** — Flags potential conflicts to prevent scheduling errors
- **Example:** If two tasks are both scheduled for "MORNING," the system warns the owner

## Testing PawPal+

PawPal+ includes a comprehensive automated test suite to verify all functionality:

### Running Tests

```bash
python -m pytest tests/test_pawpal.py -v
```

### Test Coverage

The test suite includes **26 automated tests** covering:

- **Task Management** (6 tests) — Adding, removing, and marking tasks complete
- **Owner & Pet Management** (3 tests) — Managing pets and owner-level tasks
- **Core Scheduling** (3 tests) — Priority-based scheduling and time constraints
- **Sorting Logic** (2 tests) — Sorting by time of day and priority
- **Filtering Logic** (2 tests) — Filtering by completion status and priority
- **Recurring Tasks** (3 tests) — Daily, weekly, and one-time task automation
- **Conflict Detection** (3 tests) — Detecting and reporting scheduling conflicts

### Confidence Level

**⭐⭐⭐⭐⭐ (5/5 stars)**

- All 26 tests pass consistently
- Core algorithms (sorting, filtering, scheduling) verified
- Recurring task automation working correctly
- Conflict detection functioning as designed
- Edge cases handled (empty task lists, single tasks, etc.)

The system is production-ready for basic pet care scheduling needs!

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
