"""
PawPal+ Demo Script
Tests the pet care scheduling system with a realistic scenario.
"""

from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Category, TimeOfDay


def main():
    """Run a demo of the PawPal+ scheduling system."""

    # Create an owner
    owner = Owner(
        name="Sarah",
        available_hours_per_day=3.0,  # 3 hours available for pet care
        preferences={"prefers_morning": True}
    )

    # Create pets
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

    # Add pets to owner
    owner.add_pet(dog)
    owner.add_pet(cat)

    # Create tasks for the dog
    dog_walk = Task(
        name="Morning Walk",
        duration=30,
        priority=Priority.HIGH,
        category=Category.WALK,
        time_of_day=TimeOfDay.MORNING
    )

    dog_feeding = Task(
        name="Dog Breakfast",
        duration=15,
        priority=Priority.HIGH,
        category=Category.FEEDING,
        time_of_day=TimeOfDay.MORNING
    )

    dog_play = Task(
        name="Dog Playtime",
        duration=20,
        priority=Priority.MEDIUM,
        category=Category.PLAY,
        time_of_day=TimeOfDay.AFTERNOON
    )

    # Add tasks to dog
    dog.add_task(dog_walk)
    dog.add_task(dog_feeding)
    dog.add_task(dog_play)

    # Create tasks for the cat
    cat_medication = Task(
        name="Cat Medication",
        duration=10,
        priority=Priority.HIGH,
        category=Category.MEDICATION,
        time_of_day=TimeOfDay.MORNING
    )

    cat_feeding = Task(
        name="Cat Feeding",
        duration=10,
        priority=Priority.HIGH,
        category=Category.FEEDING,
        time_of_day=TimeOfDay.EVENING
    )

    cat_grooming = Task(
        name="Cat Grooming",
        duration=25,
        priority=Priority.MEDIUM,
        category=Category.GROOMING,
        time_of_day=TimeOfDay.FLEXIBLE
    )

    # Add tasks to cat
    cat.add_task(cat_medication)
    cat.add_task(cat_feeding)
    cat.add_task(cat_grooming)

    # Add some owner-level tasks (general pet care)
    general_cleanup = Task(
        name="Litter Box Cleanup",
        duration=15,
        priority=Priority.MEDIUM,
        category=Category.OTHER,
        time_of_day=TimeOfDay.FLEXIBLE
    )
    owner.add_task(general_cleanup)

    print("\n" + "=" * 50)
    print("🐾 PawPal+ SCHEDULING DEMO 🐾")
    print("=" * 50)

    # Schedule for the dog
    print("\n--- SCHEDULING FOR MAX (Dog) ---")
    scheduler_dog = Scheduler(owner, dog)
    scheduler_dog.schedule_day()
    print(scheduler_dog.format_schedule())

    # Mark a task as complete
    dog_walk.mark_complete()
    print("\n[Task marked as complete: Morning Walk]\n")
    print(scheduler_dog.format_schedule())

    # Schedule for the cat
    print("\n\n--- SCHEDULING FOR WHISKERS (Cat) ---")
    scheduler_cat = Scheduler(owner, cat)
    scheduler_cat.schedule_day()
    print(scheduler_cat.format_schedule())

    # Show task management
    print("\n\n--- TASK MANAGEMENT DEMO ---")
    print(f"Tasks for {dog.name}: {len(dog.get_tasks())}")
    for task in dog.get_tasks():
        print(f"  - {task.name}")

    print(f"\nTasks for {cat.name}: {len(cat.get_tasks())}")
    for task in cat.get_tasks():
        print(f"  - {task.name}")

    print(f"\nOwner's general tasks: {len(owner.get_tasks())}")
    for task in owner.get_tasks():
        print(f"  - {task.name}")


if __name__ == "__main__":
    main()
