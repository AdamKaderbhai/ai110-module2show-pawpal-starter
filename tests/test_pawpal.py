"""
Tests for PawPal+ scheduling system.
Verifies core functionality of Pet, Task, Owner, and Scheduler classes.
"""

import pytest
from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Category, TimeOfDay


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