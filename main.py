"""
PawPal+ Demo Script - Phase 4
Tests the enhanced pet care scheduling system with sorting, filtering,
recurring tasks, and conflict detection.
"""

from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Category, TimeOfDay, Frequency
from datetime import datetime


def main():
    """Run a comprehensive demo of the PawPal+ scheduling system."""

    print("\n" + "=" * 60)
    print("🐾 PawPal+ ENHANCED SCHEDULING DEMO (Phase 4) 🐾")
    print("=" * 60)

    # ========================================================================
    # SETUP: Create owner, pets, and tasks
    # ========================================================================
    owner = Owner(
        name="Sarah",
        available_hours_per_day=3.0,
        preferences={"prefers_morning": True}
    )

    dog = Pet(
        name="Max",
        pet_type="Golden Retriever",
        age=3,
        special_needs=["gluten-free diet"]
    )

    cat = Pet(
        name="Whiskers",
        pet_type="Persian Cat",
        age=5,
        special_needs=["daily medication"]
    )

    owner.add_pet(dog)
    owner.add_pet(cat)

    # Create tasks for the dog with different frequencies
    dog_walk = Task(
        name="Morning Walk",
        duration=30,
        priority=Priority.HIGH,
        category=Category.WALK,
        time_of_day=TimeOfDay.MORNING,
        frequency=Frequency.DAILY
    )

    dog_feeding = Task(
        name="Dog Breakfast",
        duration=15,
        priority=Priority.HIGH,
        category=Category.FEEDING,
        time_of_day=TimeOfDay.MORNING,
        frequency=Frequency.DAILY
    )

    dog_play = Task(
        name="Dog Playtime",
        duration=20,
        priority=Priority.MEDIUM,
        category=Category.PLAY,
        time_of_day=TimeOfDay.AFTERNOON,
        frequency=Frequency.DAILY
    )

    dog_grooming = Task(
        name="Dog Grooming",
        duration=45,
        priority=Priority.MEDIUM,
        category=Category.GROOMING,
        time_of_day=TimeOfDay.AFTERNOON,  # Conflict with playtime!
        frequency=Frequency.WEEKLY
    )

    dog.add_task(dog_walk)
    dog.add_task(dog_feeding)
    dog.add_task(dog_play)
    dog.add_task(dog_grooming)

    # Create tasks for the cat
    cat_medication = Task(
        name="Cat Medication",
        duration=10,
        priority=Priority.HIGH,
        category=Category.MEDICATION,
        time_of_day=TimeOfDay.MORNING,
        frequency=Frequency.DAILY
    )

    cat_feeding = Task(
        name="Cat Feeding",
        duration=10,
        priority=Priority.HIGH,
        category=Category.FEEDING,
        time_of_day=TimeOfDay.EVENING,
        frequency=Frequency.DAILY
    )

    cat_grooming = Task(
        name="Cat Grooming",
        duration=25,
        priority=Priority.MEDIUM,
        category=Category.GROOMING,
        time_of_day=TimeOfDay.FLEXIBLE,
        frequency=Frequency.WEEKLY
    )

    cat.add_task(cat_medication)
    cat.add_task(cat_feeding)
    cat.add_task(cat_grooming)

    # ========================================================================
    # DEMO 1: Basic Scheduling
    # ========================================================================
    print("\n" + "-" * 60)
    print("DEMO 1: Basic Schedule for Max (Dog)")
    print("-" * 60)

    scheduler_dog = Scheduler(owner, dog)
    scheduler_dog.schedule_day()
    print(scheduler_dog.format_schedule())

    # ========================================================================
    # DEMO 2: Conflict Detection
    # ========================================================================
    print("\n" + "-" * 60)
    print("DEMO 2: Conflict Detection")
    print("-" * 60)

    conflicts = scheduler_dog.detect_conflicts()
    if conflicts:
        print("⚠️ Conflicts Detected:")
        for conflict in conflicts:
            print(f"  • {conflict}")
    else:
        print("✅ No conflicts detected!")

    # ========================================================================
    # DEMO 3: Filtering by Status
    # ========================================================================
    print("\n" + "-" * 60)
    print("DEMO 3: Filtering by Completion Status")
    print("-" * 60)

    # Mark some tasks as complete
    dog_walk.mark_complete()
    dog_feeding.mark_complete()

    completed_tasks = scheduler_dog.filter_by_status(completed=True)
    pending_tasks = scheduler_dog.filter_by_status(completed=False)

    print(f"✅ Completed Tasks ({len(completed_tasks)}):")
    for task in completed_tasks:
        print(f"  • {task.name} ({task.duration} min)")

    print(f"\n⏳ Pending Tasks ({len(pending_tasks)}):")
    for task in pending_tasks:
        print(f"  • {task.name} ({task.duration} min)")

    # ========================================================================
    # DEMO 4: Filtering by Priority
    # ========================================================================
    print("\n" + "-" * 60)
    print("DEMO 4: Filtering by Priority")
    print("-" * 60)

    high_priority = scheduler_dog.filter_by_priority(Priority.HIGH)
    medium_priority = scheduler_dog.filter_by_priority(Priority.MEDIUM)
    low_priority = scheduler_dog.filter_by_priority(Priority.LOW)

    print(f"🔴 HIGH Priority Tasks ({len(high_priority)}):")
    for task in high_priority:
        print(f"  • {task.name}")

    print(f"\n🟡 MEDIUM Priority Tasks ({len(medium_priority)}):")
    for task in medium_priority:
        print(f"  • {task.name}")

    print(f"\n🟢 LOW Priority Tasks ({len(low_priority)}):")
    for task in low_priority:
        print(f"  • {task.name}")

    # ========================================================================
    # DEMO 5: Sorting by Time of Day
    # ========================================================================
    print("\n" + "-" * 60)
    print("DEMO 5: Tasks Sorted by Time of Day")
    print("-" * 60)

    sorted_by_time = scheduler_dog.sort_by_time()
    for i, task in enumerate(sorted_by_time, 1):
        print(f"{i}. {task.name:20} → {task.time_of_day.value}")

    # ========================================================================
    # DEMO 6: Recurring Tasks
    # ========================================================================
    print("\n" + "-" * 60)
    print("DEMO 6: Recurring Task Automation")
    print("-" * 60)

    print(f"\nOriginal Task: {dog_walk.name}")
    print(f"  Frequency: {dog_walk.frequency.value}")
    print(f"  Scheduled Date: {dog_walk.scheduled_date}")

    # Create next occurrence
    next_occurrence = dog_walk.create_next_occurrence()
    if next_occurrence:
        print(f"\nNext Occurrence Created:")
        print(f"  Task: {next_occurrence.name}")
        print(f"  Scheduled Date: {next_occurrence.scheduled_date}")
        print(f"  (Tomorrow's date)")
    else:
        print("No next occurrence (task is not recurring)")

    # ========================================================================
    # DEMO 7: Schedule for Cat with Conflict Detection
    # ========================================================================
    print("\n" + "-" * 60)
    print("DEMO 7: Schedule for Whiskers (Cat)")
    print("-" * 60)

    scheduler_cat = Scheduler(owner, cat)
    scheduler_cat.schedule_day()
    print(scheduler_cat.format_schedule())

    conflicts_cat = scheduler_cat.detect_conflicts()
    if conflicts_cat:
        print("\n⚠️ Conflicts Detected:")
        for conflict in conflicts_cat:
            print(f"  • {conflict}")
    else:
        print("\n✅ No conflicts detected!")

    # ========================================================================
    # DEMO 8: Summary Statistics
    # ========================================================================
    print("\n" + "-" * 60)
    print("DEMO 8: System Summary")
    print("-" * 60)

    total_tasks = sum(len(pet.get_tasks()) for pet in owner.pets)
    print(f"👤 Owner: {owner.name}")
    print(f"🐾 Pets: {len(owner.pets)}")
    print(f"✅ Total Tasks: {total_tasks}")
    print(f"⏰ Available Time: {owner.available_hours_per_day} hours/day")

    daily_tasks = sum(
        1 for pet in owner.pets
        for task in pet.get_tasks()
        if task.frequency == Frequency.DAILY
    )
    weekly_tasks = sum(
        1 for pet in owner.pets
        for task in pet.get_tasks()
        if task.frequency == Frequency.WEEKLY
    )

    print(f"\n📅 Task Frequency Breakdown:")
    print(f"  Daily: {daily_tasks}")
    print(f"  Weekly: {weekly_tasks}")

    print("\n" + "=" * 60)
    print("✨ Demo Complete! ✨")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
