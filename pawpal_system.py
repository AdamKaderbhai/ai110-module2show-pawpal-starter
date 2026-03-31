"""
PawPal+ System Logic
Defines the core classes for managing pet owners, pets, tasks, and scheduling.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class Priority(Enum):
    """Priority levels for tasks."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Category(Enum):
    """Categories of pet care tasks."""
    WALK = "walk"
    FEEDING = "feeding"
    GROOMING = "grooming"
    MEDICATION = "medication"
    ENRICHMENT = "enrichment"
    PLAY = "play"
    SLEEP = "sleep"
    OTHER = "other"


class TimeOfDay(Enum):
    """Time preferences for tasks."""
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    FLEXIBLE = "flexible"


@dataclass
class Pet:
    """Represents a pet with basic information."""
    name: str
    pet_type: str  # e.g., "dog", "cat", "rabbit"
    age: int
    special_needs: List[str] = field(default_factory=list)  # e.g., ["allergies", "medications"]
    tasks: List['Task'] = field(default_factory=list)

    def add_task(self, task: 'Task') -> None:
        """Add a task to the pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_name: str) -> None:
        """Remove a task by name from the pet's task list."""
        self.tasks = [task for task in self.tasks if task.name != task_name]

    def get_tasks(self) -> List['Task']:
        """Return all tasks for the pet."""
        return self.tasks


@dataclass
class Task:
    """Represents a care task that needs to be scheduled."""
    name: str
    duration: float  # in minutes
    priority: Priority
    category: Category
    time_of_day: TimeOfDay = TimeOfDay.FLEXIBLE
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark the task as incomplete."""
        self.completed = False


@dataclass
class Owner:
    """Represents a pet owner who manages pets and tasks."""
    name: str
    available_hours_per_day: float  # total time available for pet care
    preferences: Dict[str, any] = field(default_factory=dict)
    pets: List[Pet] = field(default_factory=list)
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to the owner's task list."""
        self.tasks.append(task)

    def remove_task(self, task_name: str) -> None:
        """Remove a task by name."""
        self.tasks = [task for task in self.tasks if task.name != task_name]

    def get_tasks(self) -> List[Task]:
        """Return all tasks."""
        return self.tasks

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet by name from the owner's pet list."""
        self.pets = [pet for pet in self.pets if pet.name != pet_name]


class Scheduler:
    """Generates optimized daily schedules based on owner, pet, and task constraints."""

    def __init__(self, owner: Owner, pet: Pet):
        """Initialize scheduler with owner and pet."""
        self.owner = owner
        self.pet = pet
        self.scheduled_tasks: List[Task] = []

    def set_tasks(self, tasks: List[Task]) -> None:
        """Store the tasks to schedule."""
        self.scheduled_tasks = tasks.copy()

    def schedule_day(self) -> List[Task]:
        """
        Generate an optimized daily schedule respecting time and priority constraints.
        Sorts tasks by priority (HIGH > MEDIUM > LOW), then by time preference.
        Returns a list of tasks ordered for the day.
        """
        # Combine owner's tasks and pet's tasks
        all_tasks = self.owner.get_tasks() + self.pet.get_tasks()

        # Sort by priority (descending) and then by time_of_day preference
        # Priority order: HIGH (3) > MEDIUM (2) > LOW (1)
        # Time preference order: morning, afternoon, evening, flexible
        time_preference_order = {
            TimeOfDay.MORNING: 0,
            TimeOfDay.AFTERNOON: 1,
            TimeOfDay.EVENING: 2,
            TimeOfDay.FLEXIBLE: 3,
        }

        sorted_tasks = sorted(
            all_tasks,
            key=lambda task: (-task.priority.value, time_preference_order[task.time_of_day])
        )

        # Store the scheduled tasks
        self.scheduled_tasks = sorted_tasks

        return sorted_tasks

    def get_schedule(self) -> List[Task]:
        """Return the currently scheduled tasks."""
        return self.scheduled_tasks

    def format_schedule(self) -> str:
        """
        Return a nicely formatted string representation of the schedule for printing.
        """
        if not self.scheduled_tasks:
            return "No tasks scheduled for today."

        lines = ["Daily Schedule for " + self.pet.name, "=" * 40]

        current_time = 0.0
        for i, task in enumerate(self.scheduled_tasks, 1):
            status = "[COMPLETED]" if task.completed else "[PENDING]"
            lines.append(
                f"{i}. {task.name} {status}\n"
                f"   Duration: {task.duration} min | Priority: {task.priority.name} | "
                f"Time: {task.time_of_day.value} | Category: {task.category.value}"
            )
            current_time += task.duration

        lines.append("=" * 40)
        lines.append(f"Total Time Required: {current_time} minutes ({current_time / 60:.1f} hours)")
        lines.append(f"Available Time: {self.owner.available_hours_per_day} hours")

        if current_time <= self.owner.available_hours_per_day * 60:
            lines.append("Status: Schedule fits within available time ✓")
        else:
            lines.append("Status: Schedule exceeds available time ✗")

        return "\n".join(lines)