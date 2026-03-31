"""
Tests for PawPal+ scheduling system.
Verifies core functionality of Pet, Task, Owner, and Scheduler classes,
plus Phase 4 algorithmic enhancements (sorting, filtering, recurring, conflicts).
"""

import pytest
from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Category, TimeOfDay, Frequency


class TestTaskCompletion:
    """Test task completion tracking."""

    def test_mark_complete(self):
        """Verify that mark_complete() sets completed to True."""
        task = Task(
            name="Morning Walk",
            duration=30,
            priority=Priority.HIGH,
            category=Category.WALK
        )
        assert task.completed == False, "Task should start as incomplete"

        task.mark_complete()
        assert task.completed == True, "Task should be completed after mark_complete()"

    def test_mark_incomplete(self):
        """Verify that mark_incomplete() sets completed to False."""
        task = Task(
            name="Morning Walk",
            duration=30,
            priority=Priority.HIGH,
            category=Category.WALK,
            completed=True
        )
        assert task.completed == True, "Task should start as completed"

        task.mark_incomplete()
        assert task.completed == False, "Task should be incomplete after mark_incomplete()"

    def test_task_completion_toggle(self):
        """Verify toggling task completion multiple times works correctly."""
        task = Task(
            name="Feeding",
            duration=15,
            priority=Priority.HIGH,
            category=Category.FEEDING
        )

        task.mark_complete()
        assert task.completed == True

        task.mark_incomplete()
        assert task.completed == False

        task.mark_complete()
        assert task.completed == True


class TestTaskAddition:
    """Test task addition and removal."""

    def test_add_task_to_pet(self):
        """Verify that adding a task to a Pet increases the task count."""
        pet = Pet(name="Max", pet_type="Dog", age=3)
        assert len(pet.get_tasks()) == 0, "Pet should start with no tasks"

        task = Task(
            name="Walk",
            duration=30,
            priority=Priority.HIGH,
            category=Category.WALK
        )
        pet.add_task(task)

        assert len(pet.get_tasks()) == 1, "Pet should have 1 task after adding"
        assert pet.get_tasks()[0].name == "Walk", "Task name should match"

    def test_add_multiple_tasks_to_pet(self):
        """Verify adding multiple tasks to a pet."""
        pet = Pet(name="Whiskers", pet_type="Cat", age=5)

        tasks = [
            Task("Feed", 15, Priority.HIGH, Category.FEEDING),
            Task("Groom", 25, Priority.MEDIUM, Category.GROOMING),
            Task("Play", 20, Priority.LOW, Category.PLAY)
        ]

        for task in tasks:
            pet.add_task(task)

        assert len(pet.get_tasks()) == 3, "Pet should have 3 tasks"

    def test_remove_task_from_pet(self):
        """Verify removing a task from a pet decreases the task count."""
        pet = Pet(name="Max", pet_type="Dog", age=3)

        task1 = Task("Walk", 30, Priority.HIGH, Category.WALK)
        task2 = Task("Feed", 15, Priority.HIGH, Category.FEEDING)

        pet.add_task(task1)
        pet.add_task(task2)
        assert len(pet.get_tasks()) == 2

        pet.remove_task("Walk")
        assert len(pet.get_tasks()) == 1, "Pet should have 1 task after removal"
        assert pet.get_tasks()[0].name == "Feed", "Remaining task should be Feed"


class TestOwnerManagement:
    """Test owner management of pets and tasks."""

    def test_add_pet_to_owner(self):
        """Verify adding a pet to an owner."""
        owner = Owner(name="Sarah", available_hours_per_day=3.0)
        assert len(owner.pets) == 0, "Owner should start with no pets"

        pet = Pet(name="Max", pet_type="Dog", age=3)
        owner.add_pet(pet)

        assert len(owner.pets) == 1, "Owner should have 1 pet"
        assert owner.pets[0].name == "Max", "Pet name should match"

    def test_add_task_to_owner(self):
        """Verify adding a task to an owner."""
        owner = Owner(name="Sarah", available_hours_per_day=3.0)
        assert len(owner.get_tasks()) == 0, "Owner should start with no tasks"

        task = Task("Cleanup", 15, Priority.MEDIUM, Category.OTHER)
        owner.add_task(task)

        assert len(owner.get_tasks()) == 1, "Owner should have 1 task"

    def test_remove_pet_from_owner(self):
        """Verify removing a pet from an owner."""
        owner = Owner(name="Sarah", available_hours_per_day=3.0)

        dog = Pet(name="Max", pet_type="Dog", age=3)
        cat = Pet(name="Whiskers", pet_type="Cat", age=5)

        owner.add_pet(dog)
        owner.add_pet(cat)
        assert len(owner.pets) == 2

        owner.remove_pet("Max")
        assert len(owner.pets) == 1, "Owner should have 1 pet after removal"


class TestScheduler:
    """Test the scheduling logic."""

    def test_schedule_by_priority(self):
        """Verify tasks are scheduled by priority (HIGH > MEDIUM > LOW)."""
        owner = Owner(name="Sarah", available_hours_per_day=3.0)
        pet = Pet(name="Max", pet_type="Dog", age=3)

        low_priority = Task("Low", 10, Priority.LOW, Category.PLAY)
        high_priority = Task("High", 10, Priority.HIGH, Category.WALK)
        medium_priority = Task("Medium", 10, Priority.MEDIUM, Category.FEEDING)

        pet.add_task(low_priority)
        pet.add_task(high_priority)
        pet.add_task(medium_priority)

        scheduler = Scheduler(owner, pet)
        scheduled = scheduler.schedule_day()

        assert scheduled[0].priority == Priority.HIGH, "First task should be HIGH priority"
        assert scheduled[1].priority == Priority.MEDIUM, "Second task should be MEDIUM priority"
        assert scheduled[2].priority == Priority.LOW, "Third task should be LOW priority"

    def test_schedule_respects_time_constraints(self):
        """Verify schedule total time doesn't exceed available hours."""
        owner = Owner(name="Sarah", available_hours_per_day=1.0)  # Only 1 hour
        pet = Pet(name="Max", pet_type="Dog", age=3)

        # Add tasks totaling 50 minutes (fits in 1 hour)
        pet.add_task(Task("Walk", 30, Priority.HIGH, Category.WALK))
        pet.add_task(Task("Feed", 20, Priority.HIGH, Category.FEEDING))

        scheduler = Scheduler(owner, pet)
        scheduled = scheduler.schedule_day()

        total_minutes = sum(task.duration for task in scheduled)
        available_minutes = owner.available_hours_per_day * 60

        assert total_minutes <= available_minutes, "Total task time should fit in available hours"

    def test_get_schedule(self):
        """Verify get_schedule returns the scheduled tasks."""
        owner = Owner(name="Sarah", available_hours_per_day=3.0)
        pet = Pet(name="Max", pet_type="Dog", age=3)

        task = Task("Walk", 30, Priority.HIGH, Category.WALK)
        pet.add_task(task)

        scheduler = Scheduler(owner, pet)
        scheduler.schedule_day()

        schedule = scheduler.get_schedule()
        assert len(schedule) > 0, "Schedule should not be empty"
        assert schedule[0].name == "Walk", "Schedule should contain the walk task"


# ============================================================================
# PHASE 4: ALGORITHMIC ENHANCEMENTS
# ============================================================================

class TestSortingLogic:
    """Test sorting algorithms (Phase 4)."""

    def test_sort_by_time_order(self):
        """Verify sort_by_time() returns tasks in correct time order."""
        owner = Owner(name="Sarah", available_hours_per_day=3.0)
        pet = Pet(name="Max", pet_type="Dog", age=3)

        # Add tasks out of order
        pet.add_task(Task("Evening Task", 10, Priority.LOW, Category.PLAY, TimeOfDay.EVENING))
        pet.add_task(Task("Morning Task", 10, Priority.LOW, Category.WALK, TimeOfDay.MORNING))
        pet.add_task(Task("Afternoon Task", 10, Priority.LOW, Category.FEEDING, TimeOfDay.AFTERNOON))
        pet.add_task(Task("Flexible Task", 10, Priority.LOW, Category.PLAY, TimeOfDay.FLEXIBLE))

        scheduler = Scheduler(owner, pet)
        scheduler.schedule_day()  # Must call schedule_day() first to populate scheduled_tasks
        sorted_tasks = scheduler.sort_by_time()

        # Verify order: morning → afternoon → evening → flexible
        assert sorted_tasks[0].time_of_day == TimeOfDay.MORNING
        assert sorted_tasks[1].time_of_day == TimeOfDay.AFTERNOON
        assert sorted_tasks[2].time_of_day == TimeOfDay.EVENING
        assert sorted_tasks[3].time_of_day == TimeOfDay.FLEXIBLE

    def test_sort_by_priority_order(self):
        """Verify sort_by_priority() returns tasks in descending priority order."""
        owner = Owner(name="Sarah", available_hours_per_day=3.0)
        pet = Pet(name="Max", pet_type="Dog", age=3)

        # Add tasks out of priority order
        pet.add_task(Task("Low", 10, Priority.LOW, Category.PLAY))
        pet.add_task(Task("High", 10, Priority.HIGH, Category.WALK))
        pet.add_task(Task("Medium", 10, Priority.MEDIUM, Category.FEEDING))

        scheduler = Scheduler(owner, pet)
        scheduler.schedule_day()  # Must call schedule_day() first to populate scheduled_tasks
        sorted_tasks = scheduler.sort_by_priority()

        # Verify order: HIGH → MEDIUM → LOW
        assert sorted_tasks[0].priority == Priority.HIGH
        assert sorted_tasks[1].priority == Priority.MEDIUM
        assert sorted_tasks[2].priority == Priority.LOW


class TestFilteringLogic:
    """Test filtering algorithms (Phase 4)."""

    def test_filter_by_completion_status(self):
        """Verify filter_by_status() correctly separates completed and pending tasks."""
        owner = Owner(name="Sarah", available_hours_per_day=3.0)
        pet = Pet(name="Max", pet_type="Dog", age=3)

        task1 = Task("Walk", 30, Priority.HIGH, Category.WALK)
        task2 = Task("Feed", 15, Priority.HIGH, Category.FEEDING)
        task3 = Task("Play", 20, Priority.LOW, Category.PLAY)

        pet.add_task(task1)
        pet.add_task(task2)
        pet.add_task(task3)

        # Mark some as complete
        task1.mark_complete()
        task2.mark_complete()

        scheduler = Scheduler(owner, pet)
        scheduler.schedule_day()  # Must call schedule_day() first to populate scheduled_tasks
        completed = scheduler.filter_by_status(completed=True)
        pending = scheduler.filter_by_status(completed=False)

        assert len(completed) == 2, "Should have 2 completed tasks"
        assert len(pending) == 1, "Should have 1 pending task"
        assert pending[0].name == "Play", "Pending task should be Play"

    def test_filter_by_priority_level(self):
        """Verify filter_by_priority() returns only tasks of specified priority."""
        owner = Owner(name="Sarah", available_hours_per_day=3.0)
        pet = Pet(name="Max", pet_type="Dog", age=3)

        pet.add_task(Task("Walk", 30, Priority.HIGH, Category.WALK))
        pet.add_task(Task("Feed", 15, Priority.HIGH, Category.FEEDING))
        pet.add_task(Task("Groom", 45, Priority.MEDIUM, Category.GROOMING))
        pet.add_task(Task("Play", 20, Priority.LOW, Category.PLAY))

        scheduler = Scheduler(owner, pet)
        scheduler.schedule_day()  # Must call schedule_day() first to populate scheduled_tasks

        high_priority = scheduler.filter_by_priority(Priority.HIGH)
        medium_priority = scheduler.filter_by_priority(Priority.MEDIUM)
        low_priority = scheduler.filter_by_priority(Priority.LOW)

        assert len(high_priority) == 2
        assert len(medium_priority) == 1
        assert len(low_priority) == 1


class TestRecurringTasks:
    """Test recurring task automation (Phase 4)."""

    def test_daily_task_creates_next_occurrence(self):
        """Verify daily tasks create a new task for tomorrow."""
        task = Task(
            name="Morning Walk",
            duration=30,
            priority=Priority.HIGH,
            category=Category.WALK,
            frequency=Frequency.DAILY
        )

        next_task = task.create_next_occurrence()

        assert next_task is not None, "Daily task should create next occurrence"
        assert next_task.name == "Morning Walk"
        assert next_task.duration == 30
        assert next_task.priority == Priority.HIGH
        assert next_task.frequency == Frequency.DAILY
        assert next_task.scheduled_date is not None

    def test_weekly_task_creates_next_occurrence(self):
        """Verify weekly tasks create a new task for next week."""
        task = Task(
            name="Weekly Grooming",
            duration=60,
            priority=Priority.MEDIUM,
            category=Category.GROOMING,
            frequency=Frequency.WEEKLY,
            scheduled_date=datetime(2026, 3, 30).date()
        )

        next_task = task.create_next_occurrence()

        assert next_task is not None, "Weekly task should create next occurrence"
        assert next_task.frequency == Frequency.WEEKLY
        # Next occurrence should be 7 days later
        expected_date = datetime(2026, 4, 6).date()
        assert next_task.scheduled_date == expected_date

    def test_once_task_no_recurrence(self):
        """Verify 'once' frequency tasks don't create next occurrence."""
        task = Task(
            name="One-time Vet Visit",
            duration=60,
            priority=Priority.HIGH,
            category=Category.OTHER,
            frequency=Frequency.ONCE
        )

        next_task = task.create_next_occurrence()

        assert next_task is None, "One-time task should not create next occurrence"


class TestConflictDetection:
    """Test conflict detection (Phase 4)."""

    def test_detect_same_time_conflict(self):
        """Verify system detects tasks scheduled at same time."""
        owner = Owner(name="Sarah", available_hours_per_day=3.0)
        pet = Pet(name="Max", pet_type="Dog", age=3)

        # Add two tasks at the same time
        pet.add_task(Task("Morning Walk", 30, Priority.HIGH, Category.WALK, TimeOfDay.MORNING))
        pet.add_task(Task("Dog Breakfast", 15, Priority.HIGH, Category.FEEDING, TimeOfDay.MORNING))

        scheduler = Scheduler(owner, pet)
        scheduler.schedule_day()  # Must call schedule_day() first to populate scheduled_tasks
        conflicts = scheduler.detect_conflicts()

        assert len(conflicts) > 0, "Should detect conflict for same time"
        assert any("Morning Walk" in conflict and "Dog Breakfast" in conflict for conflict in conflicts)

    def test_no_conflict_different_times(self):
        """Verify no conflicts detected when tasks are at different times."""
        owner = Owner(name="Sarah", available_hours_per_day=3.0)
        pet = Pet(name="Max", pet_type="Dog", age=3)

        pet.add_task(Task("Morning Walk", 30, Priority.HIGH, Category.WALK, TimeOfDay.MORNING))
        pet.add_task(Task("Afternoon Play", 20, Priority.LOW, Category.PLAY, TimeOfDay.AFTERNOON))
        pet.add_task(Task("Evening Dinner", 15, Priority.HIGH, Category.FEEDING, TimeOfDay.EVENING))

        scheduler = Scheduler(owner, pet)
        conflicts = scheduler.detect_conflicts()

        assert len(conflicts) == 0, "Should not detect conflicts for different times"

    def test_no_conflict_with_empty_tasks(self):
        """Verify no conflicts with pet that has no tasks."""
        owner = Owner(name="Sarah", available_hours_per_day=3.0)
        pet = Pet(name="Max", pet_type="Dog", age=3)

        scheduler = Scheduler(owner, pet)
        conflicts = scheduler.detect_conflicts()

        assert len(conflicts) == 0, "Should have no conflicts with empty task list"