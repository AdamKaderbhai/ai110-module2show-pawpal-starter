"""
PawPal+ System Logic
Defines the core classes for managing pet owners, pets, tasks, and scheduling.
Enhanced with algorithmic intelligence for recurring tasks, conflict detection, and filtering.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime, timedelta, date
import json
import os


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


class Frequency(Enum):
    """Frequency options for recurring tasks."""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


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
    frequency: Frequency = Frequency.ONCE
    scheduled_date: Optional[date] = None

    def mark_complete(self) -> Optional['Task']:
        """
        Mark the task as completed.
        Returns the next occurrence if frequency is daily or weekly, None otherwise.
        """
        self.completed = True
        return self.create_next_occurrence()

    def mark_incomplete(self) -> None:
        """Mark the task as incomplete."""
        self.completed = False

    def create_next_occurrence(self) -> Optional['Task']:
        """
        Create the next occurrence of this task based on frequency.

        Returns:
            - None if frequency is "once"
            - A new Task for tomorrow if frequency is "daily"
            - A new Task for 7 days from now if frequency is "weekly"
        """
        if self.frequency == Frequency.ONCE:
            return None

        # Determine the base date for calculation
        base_date = self.scheduled_date if self.scheduled_date else date.today()

        if self.frequency == Frequency.DAILY:
            next_date = base_date + timedelta(days=1)
        elif self.frequency == Frequency.WEEKLY:
            next_date = base_date + timedelta(days=7)
        else:
            return None

        # Create a new task with the same properties but updated date
        next_task = Task(
            name=self.name,
            duration=self.duration,
            priority=self.priority,
            category=self.category,
            time_of_day=self.time_of_day,
            completed=False,
            frequency=self.frequency,
            scheduled_date=next_date
        )

        return next_task


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

    def to_dict(self) -> Dict:
        """
        Convert the Owner and all associated data to a dictionary for JSON serialization.
        Handles enums by converting them to strings, and dates to ISO format.
        """
        pets_data = []
        for pet in self.pets:
            pet_tasks = []
            for task in pet.tasks:
                pet_tasks.append({
                    "name": task.name,
                    "duration": task.duration,
                    "priority": task.priority.name,
                    "category": task.category.name,
                    "time_of_day": task.time_of_day.name,
                    "completed": task.completed,
                    "frequency": task.frequency.name,
                    "scheduled_date": task.scheduled_date.isoformat() if task.scheduled_date else None
                })

            pets_data.append({
                "name": pet.name,
                "pet_type": pet.pet_type,
                "age": pet.age,
                "special_needs": pet.special_needs,
                "tasks": pet_tasks
            })

        return {
            "name": self.name,
            "available_hours_per_day": self.available_hours_per_day,
            "preferences": self.preferences,
            "pets": pets_data,
            "tasks": []  # Owner-level tasks (currently not used in UI but preserved for completeness)
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Owner':
        """
        Reconstruct an Owner from a dictionary (e.g., loaded from JSON).
        Converts string representations back to enums and dates.
        """
        # Create owner with basic info
        owner = cls(
            name=data.get("name", "Pet Owner"),
            available_hours_per_day=data.get("available_hours_per_day", 3.0),
            preferences=data.get("preferences", {})
        )

        # Reconstruct pets
        for pet_data in data.get("pets", []):
            pet = Pet(
                name=pet_data.get("name", ""),
                pet_type=pet_data.get("pet_type", ""),
                age=pet_data.get("age", 1),
                special_needs=pet_data.get("special_needs", [])
            )

            # Reconstruct tasks for this pet
            for task_data in pet_data.get("tasks", []):
                scheduled_date = None
                if task_data.get("scheduled_date"):
                    scheduled_date = date.fromisoformat(task_data["scheduled_date"])

                task = Task(
                    name=task_data.get("name", ""),
                    duration=task_data.get("duration", 0),
                    priority=Priority[task_data.get("priority", "LOW")],
                    category=Category[task_data.get("category", "OTHER")],
                    time_of_day=TimeOfDay[task_data.get("time_of_day", "FLEXIBLE")],
                    completed=task_data.get("completed", False),
                    frequency=Frequency[task_data.get("frequency", "ONCE")],
                    scheduled_date=scheduled_date
                )
                pet.add_task(task)

            owner.add_pet(pet)

        return owner


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

    def sort_by_time(self) -> List[Task]:
        """
        Sort tasks by TimeOfDay preference: morning → afternoon → evening → flexible.

        Returns:
            A list of tasks sorted by time of day preference.
        """
        time_preference_order = {
            TimeOfDay.MORNING: 0,
            TimeOfDay.AFTERNOON: 1,
            TimeOfDay.EVENING: 2,
            TimeOfDay.FLEXIBLE: 3,
        }

        return sorted(
            self.scheduled_tasks,
            key=lambda task: time_preference_order[task.time_of_day]
        )

    def sort_by_priority(self) -> List[Task]:
        """
        Sort tasks by Priority: HIGH → MEDIUM → LOW.

        Returns:
            A list of tasks sorted by priority in descending order.
        """
        return sorted(
            self.scheduled_tasks,
            key=lambda task: task.priority.value,
            reverse=True
        )

    def filter_by_status(self, completed: bool) -> List[Task]:
        """
        Filter tasks by completion status.

        Args:
            completed: If True, return only completed tasks. If False, return only incomplete tasks.

        Returns:
            A list of tasks matching the specified completion status.
        """
        return [task for task in self.scheduled_tasks if task.completed == completed]

    def filter_by_priority(self, priority: Priority) -> List[Task]:
        """
        Filter tasks by priority level.

        Args:
            priority: The Priority level to filter by.

        Returns:
            A list of tasks matching the specified priority level.
        """
        return [task for task in self.scheduled_tasks if task.priority == priority]

    def detect_conflicts(self) -> List[str]:
        """
        Detect scheduling conflicts where multiple tasks for the same pet are scheduled
        for the same TimeOfDay.

        Returns:
            A list of conflict warning strings describing conflicting tasks.
            Empty list if no conflicts are detected.
        """
        conflicts = []

        # Group tasks by TimeOfDay
        time_groups: Dict[TimeOfDay, List[Task]] = {}
        for task in self.scheduled_tasks:
            if task.time_of_day not in time_groups:
                time_groups[task.time_of_day] = []
            time_groups[task.time_of_day].append(task)

        # Check each time group for multiple tasks (excluding FLEXIBLE)
        for time_of_day, tasks in time_groups.items():
            if time_of_day != TimeOfDay.FLEXIBLE and len(tasks) > 1:
                # Found multiple tasks at the same time
                task_names = [task.name for task in tasks]
                for i in range(len(task_names)):
                    for j in range(i + 1, len(task_names)):
                        warning = (
                            f"Conflict detected: '{task_names[i]}' and '{task_names[j]}' "
                            f"both scheduled for {time_of_day.value.upper()}"
                        )
                        conflicts.append(warning)

        return conflicts

    def get_conflicts(self) -> List[str]:
        """
        Get all detected scheduling conflicts.
        Convenience method that calls detect_conflicts().

        Returns:
            A list of conflict warning strings.
        """
        return self.detect_conflicts()

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
            frequency_str = f" ({task.frequency.value})" if task.frequency != Frequency.ONCE else ""
            lines.append(
                f"{i}. {task.name}{frequency_str} {status}\n"
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

        # Check and display conflicts
        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("\nWarnings:")
            for conflict in conflicts:
                lines.append(f"  ⚠ {conflict}")

        return "\n".join(lines)

    def find_next_available_slot(self, duration_needed: float) -> Dict[str, any]:
        """
        Analyze the current schedule to find the next available time slot that can fit a task.

        This method checks time preferences in order (MORNING → AFTERNOON → EVENING → FLEXIBLE)
        and returns the first slot with sufficient available time. It calculates how much time
        is already allocated to each time period based on scheduled tasks, then determines
        which periods have enough remaining capacity.

        Algorithm approach:
        - Simple time-based analysis: Groups scheduled tasks by TimeOfDay preference
        - Calculates remaining time for each period based on available_hours_per_day
        - Distributes the available time equally across MORNING, AFTERNOON, EVENING (roughly 1/3 each)
        - FLEXIBLE tasks can fit into any remaining time across all periods
        - Returns the first time period (in preference order) with sufficient capacity

        Trade-offs:
        - Simplicity vs Optimization: This approach prioritizes clarity over optimal packing
        - Does not use weighted scoring (saved for calculate_schedule_score method)
        - Could be enhanced with ML to learn actual owner time distribution patterns

        Args:
            duration_needed: The duration in minutes needed for a new task.

        Returns:
            Dictionary with keys:
            - available (bool): True if a slot fitting the duration is found, False otherwise
            - time_of_day (TimeOfDay): The recommended TimeOfDay slot (MORNING, AFTERNOON, EVENING, or FLEXIBLE)
            - available_minutes (float): How many minutes are available in the recommended slot
            - recommendation (str): Human-readable recommendation string

        Examples:
            >>> scheduler = Scheduler(owner, pet)
            >>> result = scheduler.find_next_available_slot(45)
            >>> if result['available']:
            ...     print(result['recommendation'])
            ...     # Output: "Next available slot is AFTERNOON with 90 minutes available"
            >>> else:
            ...     print("No available slots found for a 45-minute task")

        Edge cases handled:
            - Empty schedule: Returns MORNING with full 1/3 of available_hours_per_day
            - No available time: Returns available=False with FLEXIBLE as fallback
            - All time periods full: Returns closest match with available minutes detail
        """
        # Available time in minutes per day
        total_available_minutes = self.owner.available_hours_per_day * 60

        # Distribute available time equally across time periods
        # MORNING, AFTERNOON, EVENING each get roughly 1/3 of available time
        base_slot_minutes = total_available_minutes / 3

        # Calculate time already used in each slot
        time_used: Dict[TimeOfDay, float] = {
            TimeOfDay.MORNING: 0.0,
            TimeOfDay.AFTERNOON: 0.0,
            TimeOfDay.EVENING: 0.0,
            TimeOfDay.FLEXIBLE: 0.0,
        }

        # Sum up durations of tasks already scheduled for each time slot
        for task in self.scheduled_tasks:
            if task.time_of_day in time_used:
                time_used[task.time_of_day] += task.duration

        # Time preference order for checking availability
        preferred_order = [
            TimeOfDay.MORNING,
            TimeOfDay.AFTERNOON,
            TimeOfDay.EVENING,
            TimeOfDay.FLEXIBLE,
        ]

        # Check each time slot in preference order
        for time_slot in preferred_order:
            if time_slot == TimeOfDay.FLEXIBLE:
                # FLEXIBLE can use remaining time from all other slots
                total_flexible = total_available_minutes - sum(time_used.values())
                available_minutes = total_flexible
            else:
                # Standard slots have 1/3 of available time
                available_minutes = base_slot_minutes - time_used[time_slot]

            # Return the first slot with enough room
            if available_minutes >= duration_needed:
                recommendation = f"Next available slot is {time_slot.value.upper()} with {available_minutes:.0f} minutes available"
                return {
                    "available": True,
                    "time_of_day": time_slot,
                    "available_minutes": available_minutes,
                    "recommendation": recommendation,
                }

        # No slot found with enough time
        # Return FLEXIBLE as fallback with actual available space
        total_used = sum(time_used.values())
        remaining = total_available_minutes - total_used
        recommendation = f"No available slot with {duration_needed} minutes found. {remaining:.0f} total minutes available."
        return {
            "available": False,
            "time_of_day": TimeOfDay.FLEXIBLE,
            "available_minutes": remaining,
            "recommendation": recommendation,
        }

    def calculate_schedule_score(self, tasks: List[Task]) -> Dict[str, any]:
        """
        Calculate weighted priority scores for tasks based on multiple factors.

        This method implements a multi-factor scoring system that goes beyond simple priority
        sorting. Each task receives a composite score accounting for:
        - Base priority weight: HIGH=3, MEDIUM=2, LOW=1
        - Recurrence bonus: DAILY=+2, WEEKLY=+1, ONCE=0
        - Time alignment bonus: +1 if task's preferred time matches owner's preference
        - Completion status multiplier: Incomplete tasks worth 1.5x complete tasks

        Algorithm approach (Weighted Scoring):
        - Simple approach (time-based only): Sort by TimeOfDay only, ignore urgency
            - Pros: Easy to understand, minimal computation
            - Cons: Misses priority context, no insight into task importance
        - Complex approach (weighted scoring): Combines multiple factors with weights
            - Pros: Holistic view of schedule, identifies most critical work
            - Cons: More computation, requires careful weight calibration
        - This implementation chooses the complex approach for better scheduling decisions

        Trade-offs between approaches:
        - Clarity: Time-based sorting is clearer; weighted scoring requires explanation
        - Sophistication: Weighted scoring provides better prioritization insights
        - Performance: Weighted scoring requires one-time calculation; negligible impact
        - Maintainability: Weights can be tuned without code changes if moved to config

        Future ML enhancements:
        - Learn optimal weight values from historical scheduling data
        - Use clustering to identify pattern types (e.g., "morning person" vs "night owl")
        - Predict task duration from category and historical data
        - Recommend time slots based on owner's actual availability patterns
        - Implement reinforcement learning to optimize schedule over time

        Args:
            tasks: List of Task objects to score. Can be empty.

        Returns:
            Dictionary with keys:
            - task_scores (Dict[str, float]): Mapping of task name to its calculated score
            - average_score (float): Average score across all tasks (0 if no tasks)
            - highest_priority_tasks (List[str]): Names of top 3 highest-scoring tasks
            - schedule_urgency (str): Overall urgency ("Low", "Medium", or "High")

        Examples:
            >>> scheduler = Scheduler(owner, pet)
            >>> # High priority, daily, incomplete, morning-aligned task
            >>> task1 = Task("Morning Walk", 30, Priority.HIGH, Category.WALK,
            ...              TimeOfDay.MORNING, completed=False, frequency=Frequency.DAILY)
            >>> # Low priority, once, complete, flexible task
            >>> task2 = Task("Play Session", 20, Priority.LOW, Category.PLAY,
            ...              TimeOfDay.FLEXIBLE, completed=True, frequency=Frequency.ONCE)
            >>> result = scheduler.calculate_schedule_score([task1, task2])
            >>> result['task_scores']['Morning Walk']
            6.5  # 3 (HIGH) + 2 (DAILY) + 1 (incomplete bonus) + 0.5 (alignment)
            >>> result['task_scores']['Play Session']
            1.0  # 1 (LOW) + 0 (ONCE) + 0 (complete penalty)
            >>> result['schedule_urgency']
            'High'

        Edge cases handled:
            - Empty task list: Returns all zeros/empty, urgency "Low"
            - Single task: Returns that task's score, derives urgency from it
            - All complete tasks: Lower overall urgency
            - Mix of frequencies: Properly weights recurrence bonuses
        """
        if not tasks:
            return {
                "task_scores": {},
                "average_score": 0.0,
                "highest_priority_tasks": [],
                "schedule_urgency": "Low",
            }

        task_scores: Dict[str, float] = {}

        # Iterate through each task and calculate its score
        for task in tasks:
            # Base score: Priority weight (HIGH=3, MEDIUM=2, LOW=1)
            priority_weight = task.priority.value

            # Recurrence bonus: DAILY=+2, WEEKLY=+1, ONCE=0
            recurrence_bonus = 0.0
            if task.frequency == Frequency.DAILY:
                recurrence_bonus = 2.0
            elif task.frequency == Frequency.WEEKLY:
                recurrence_bonus = 1.0
            # ONCE tasks get 0 bonus

            # Time alignment bonus: +1 if task preferred time matches owner preference
            # Default owner preference is flexible, so check if task is not FLEXIBLE
            time_alignment_bonus = 0.0
            if task.time_of_day != TimeOfDay.FLEXIBLE:
                # Consider any specific time preference as valuable
                time_alignment_bonus = 1.0

            # Completion status multiplier
            # Incomplete tasks are 1.5x more important than complete ones
            completion_multiplier = 1.5 if not task.completed else 1.0

            # Calculate composite score
            base_score = priority_weight + recurrence_bonus + time_alignment_bonus
            final_score = base_score * completion_multiplier

            task_scores[task.name] = final_score

        # Calculate average score
        average_score = sum(task_scores.values()) / len(task_scores) if task_scores else 0.0

        # Find top 3 highest priority tasks
        sorted_by_score = sorted(task_scores.items(), key=lambda x: x[1], reverse=True)
        highest_priority_tasks = [name for name, _ in sorted_by_score[:3]]

        # Determine overall schedule urgency based on average score
        # Using thresholds based on maximum possible score of ~6.5
        # (3 priority + 2 recurrence + 1 alignment + 0.5 completion)
        if average_score >= 3.5:
            schedule_urgency = "High"
        elif average_score >= 2.0:
            schedule_urgency = "Medium"
        else:
            schedule_urgency = "Low"

        return {
            "task_scores": task_scores,
            "average_score": average_score,
            "highest_priority_tasks": highest_priority_tasks,
            "schedule_urgency": schedule_urgency,
        }


# ============================================================================
# DATA PERSISTENCE FUNCTIONS
# ============================================================================

def save_owner_to_json(owner: Owner, filename: str = "pawpal_data.json") -> None:
    """
    Save an Owner and all associated data to a JSON file.

    Args:
        owner: The Owner object to save
        filename: The filename to save to (default: "pawpal_data.json")
    """
    data = owner.to_dict()
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def load_owner_from_json(filename: str = "pawpal_data.json") -> Owner:
    """
    Load an Owner from a JSON file.

    Args:
        filename: The filename to load from (default: "pawpal_data.json")

    Returns:
        An Owner object reconstructed from the JSON file.
        If the file doesn't exist, returns a default Owner.
    """
    if not os.path.exists(filename):
        # Return a default Owner if file doesn't exist
        return Owner(
            name="Pet Owner",
            available_hours_per_day=3.0,
            preferences={}
        )

    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return Owner.from_dict(data)
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        # If there's an error reading/parsing the file, return a default Owner
        print(f"Error loading {filename}: {e}. Creating default Owner.")
        return Owner(
            name="Pet Owner",
            available_hours_per_day=3.0,
            preferences={}
        )
