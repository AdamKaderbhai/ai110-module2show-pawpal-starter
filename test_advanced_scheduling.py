"""
Test suite for advanced scheduling algorithms in PawPal+ Scheduler class.
Demonstrates Challenge 1 (find_next_available_slot) and Challenge 3 (calculate_schedule_score).
"""

from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Category, TimeOfDay, Frequency


def test_find_next_available_slot():
    """Test Challenge 1: Find Next Available Time Slot."""
    print("\n" + "=" * 70)
    print("TEST 1: find_next_available_slot()")
    print("=" * 70)

    # Create owner with 3 hours available per day
    owner = Owner(name="Sarah", available_hours_per_day=3.0)
    pet = Pet(name="Max", pet_type="dog", age=3)

    scheduler = Scheduler(owner, pet)

    # Test 1.1: Empty schedule
    print("\n[Test 1.1] Empty schedule - finding 45-minute slot")
    result = scheduler.find_next_available_slot(45)
    print(f"  Available: {result['available']}")
    print(f"  Recommended time: {result['time_of_day'].value.upper()}")
    print(f"  Available minutes: {result['available_minutes']:.0f}")
    print(f"  Recommendation: {result['recommendation']}")
    assert result['available'] == True
    assert result['time_of_day'] == TimeOfDay.MORNING
    assert result['available_minutes'] == 60  # 3 hours / 3 = 60 minutes per slot

    # Test 1.2: Partially filled morning
    print("\n[Test 1.2] Morning slot partially filled (40 min used), finding 30-minute slot")
    morning_task = Task("Morning Walk", 40, Priority.HIGH, Category.WALK, TimeOfDay.MORNING)
    scheduler.set_tasks([morning_task])
    result = scheduler.find_next_available_slot(30)
    print(f"  Available: {result['available']}")
    print(f"  Recommended time: {result['time_of_day'].value.upper()}")
    print(f"  Available minutes: {result['available_minutes']:.0f}")
    print(f"  Recommendation: {result['recommendation']}")
    assert result['available'] == True
    assert result['time_of_day'] == TimeOfDay.AFTERNOON
    assert result['available_minutes'] == 60  # Afternoon untouched

    # Test 1.3: All slots nearly full
    print("\n[Test 1.3] All slots nearly full, finding 30-minute slot (should fail)")
    heavy_schedule = [
        Task("Morning Walk", 55, Priority.HIGH, Category.WALK, TimeOfDay.MORNING),
        Task("Afternoon Playtime", 55, Priority.MEDIUM, Category.PLAY, TimeOfDay.AFTERNOON),
        Task("Evening Meal", 55, Priority.HIGH, Category.FEEDING, TimeOfDay.EVENING),
    ]
    scheduler.set_tasks(heavy_schedule)
    result = scheduler.find_next_available_slot(30)
    print(f"  Available: {result['available']}")
    print(f"  Fallback time: {result['time_of_day'].value.upper()}")
    print(f"  Available minutes: {result['available_minutes']:.0f}")
    print(f"  Recommendation: {result['recommendation']}")
    assert result['available'] == False

    # Test 1.4: Exact fit scenario
    print("\n[Test 1.4] Morning has exactly 60 minutes, finding 60-minute slot")
    scheduler.set_tasks([])
    result = scheduler.find_next_available_slot(60)
    print(f"  Available: {result['available']}")
    print(f"  Recommended time: {result['time_of_day'].value.upper()}")
    print(f"  Available minutes: {result['available_minutes']:.0f}")
    assert result['available'] == True
    assert result['time_of_day'] == TimeOfDay.MORNING

    # Test 1.5: FLEXIBLE slot usage
    print("\n[Test 1.5] FLEXIBLE slots can span multiple time periods")
    flexible_task = Task("Flexible Task", 30, Priority.MEDIUM, Category.PLAY, TimeOfDay.FLEXIBLE)
    scheduler.set_tasks([flexible_task])
    result = scheduler.find_next_available_slot(45)
    print(f"  Available: {result['available']}")
    print(f"  Recommended time: {result['time_of_day'].value.upper()}")
    print(f"  Available minutes: {result['available_minutes']:.0f}")
    assert result['available'] == True

    print("\n✓ All find_next_available_slot tests passed!")


def test_calculate_schedule_score():
    """Test Challenge 3: Weighted Priority Scoring."""
    print("\n" + "=" * 70)
    print("TEST 2: calculate_schedule_score()")
    print("=" * 70)

    owner = Owner(name="Alex", available_hours_per_day=4.0)
    pet = Pet(name="Bella", pet_type="cat", age=5)
    scheduler = Scheduler(owner, pet)

    # Test 2.1: Single HIGH priority DAILY incomplete task
    print("\n[Test 2.1] HIGH priority DAILY incomplete task with MORNING preference")
    task1 = Task(
        "Morning Walk",
        30,
        Priority.HIGH,
        Category.WALK,
        TimeOfDay.MORNING,
        completed=False,
        frequency=Frequency.DAILY
    )
    result = scheduler.calculate_schedule_score([task1])
    expected_score = 3 + 2 + 1  # HIGH(3) + DAILY(2) + alignment(1) = 6, * 1.5 (incomplete) = 9.0
    print(f"  Task Score for 'Morning Walk': {result['task_scores']['Morning Walk']}")
    print(f"  Average Score: {result['average_score']:.2f}")
    print(f"  Schedule Urgency: {result['schedule_urgency']}")
    print(f"  Top Priority Tasks: {result['highest_priority_tasks']}")
    assert result['task_scores']['Morning Walk'] == 9.0
    assert result['schedule_urgency'] == "High"

    # Test 2.2: Mixed task priorities
    print("\n[Test 2.2] Mixed priorities and frequencies")
    task1 = Task("Morning Walk", 30, Priority.HIGH, Category.WALK, TimeOfDay.MORNING, completed=False, frequency=Frequency.DAILY)
    task2 = Task("Afternoon Play", 20, Priority.MEDIUM, Category.PLAY, TimeOfDay.AFTERNOON, completed=False, frequency=Frequency.WEEKLY)
    task3 = Task("Evening Cuddles", 15, Priority.LOW, Category.ENRICHMENT, TimeOfDay.FLEXIBLE, completed=True, frequency=Frequency.ONCE)

    result = scheduler.calculate_schedule_score([task1, task2, task3])

    # task1: 3 (HIGH) + 2 (DAILY) + 1 (MORNING) = 6 * 1.5 (incomplete) = 9.0
    # task2: 2 (MEDIUM) + 1 (WEEKLY) + 1 (AFTERNOON) = 4 * 1.5 (incomplete) = 6.0
    # task3: 1 (LOW) + 0 (ONCE) + 0 (FLEXIBLE) = 1 * 1.0 (complete) = 1.0

    print(f"  Task Scores:")
    for name, score in result['task_scores'].items():
        print(f"    - {name}: {score}")
    print(f"  Average Score: {result['average_score']:.2f}")
    print(f"  Top 3 Priority Tasks: {result['highest_priority_tasks']}")
    print(f"  Schedule Urgency: {result['schedule_urgency']}")

    assert result['task_scores']['Morning Walk'] == 9.0
    assert result['task_scores']['Afternoon Play'] == 6.0
    assert result['task_scores']['Evening Cuddles'] == 1.0
    assert result['highest_priority_tasks'] == ['Morning Walk', 'Afternoon Play', 'Evening Cuddles']
    assert result['schedule_urgency'] == "High"

    # Test 2.3: Empty task list
    print("\n[Test 2.3] Empty task list")
    result = scheduler.calculate_schedule_score([])
    print(f"  Task Scores: {result['task_scores']}")
    print(f"  Average Score: {result['average_score']}")
    print(f"  Schedule Urgency: {result['schedule_urgency']}")
    assert result['task_scores'] == {}
    assert result['average_score'] == 0.0
    assert result['schedule_urgency'] == "Low"

    # Test 2.4: All complete tasks (lower urgency)
    print("\n[Test 2.4] All completed tasks (lower urgency)")
    completed_tasks = [
        Task("Completed Walk", 30, Priority.HIGH, Category.WALK, TimeOfDay.MORNING, completed=True, frequency=Frequency.DAILY),
        Task("Completed Play", 20, Priority.MEDIUM, Category.PLAY, TimeOfDay.AFTERNOON, completed=True, frequency=Frequency.WEEKLY),
    ]
    result = scheduler.calculate_schedule_score(completed_tasks)
    print(f"  Task Scores:")
    for name, score in result['task_scores'].items():
        print(f"    - {name}: {score}")
    print(f"  Average Score: {result['average_score']:.2f}")
    print(f"  Schedule Urgency: {result['schedule_urgency']}")

    # completed task1: 3 + 2 + 1 = 6 * 1.0 (complete) = 6.0
    # completed task2: 2 + 1 + 1 = 4 * 1.0 (complete) = 4.0
    # average = (6.0 + 4.0) / 2 = 5.0, which is >= 3.5, so "High"
    assert result['task_scores']['Completed Walk'] == 6.0
    assert result['task_scores']['Completed Play'] == 4.0
    assert result['schedule_urgency'] == "High"

    # Test 2.5: Low priority, FLEXIBLE, ONCE frequency
    print("\n[Test 2.5] Minimum scoring task: LOW priority, ONCE, FLEXIBLE, complete")
    minimal_task = [Task("Optional Task", 10, Priority.LOW, Category.OTHER, TimeOfDay.FLEXIBLE, completed=True, frequency=Frequency.ONCE)]
    result = scheduler.calculate_schedule_score(minimal_task)
    print(f"  Task Score: {result['task_scores']['Optional Task']}")
    print(f"  Schedule Urgency: {result['schedule_urgency']}")
    assert result['task_scores']['Optional Task'] == 1.0  # 1 (LOW) + 0 + 0 = 1 * 1.0
    assert result['schedule_urgency'] == "Low"

    # Test 2.6: Highest possible score
    print("\n[Test 2.6] Maximum scoring task: HIGH priority, DAILY, time-aligned, incomplete")
    max_task = [Task("Critical Task", 15, Priority.HIGH, Category.MEDICATION, TimeOfDay.MORNING, completed=False, frequency=Frequency.DAILY)]
    result = scheduler.calculate_schedule_score(max_task)
    print(f"  Task Score: {result['task_scores']['Critical Task']}")
    print(f"  Schedule Urgency: {result['schedule_urgency']}")
    assert result['task_scores']['Critical Task'] == 9.0  # (3 + 2 + 1) * 1.5
    assert result['schedule_urgency'] == "High"

    print("\n✓ All calculate_schedule_score tests passed!")


def test_integration():
    """Integration test combining both algorithms."""
    print("\n" + "=" * 70)
    print("INTEGRATION TEST: Using both algorithms together")
    print("=" * 70)

    owner = Owner(name="Jordan", available_hours_per_day=2.5)
    pet = Pet(name="Charlie", pet_type="rabbit", age=2)
    scheduler = Scheduler(owner, pet)

    # Set up a realistic schedule
    existing_tasks = [
        Task("Morning Feed", 15, Priority.HIGH, Category.FEEDING, TimeOfDay.MORNING, completed=False, frequency=Frequency.DAILY),
        Task("Afternoon Play", 30, Priority.MEDIUM, Category.PLAY, TimeOfDay.AFTERNOON, completed=False, frequency=Frequency.DAILY),
    ]
    scheduler.set_tasks(existing_tasks)

    # Find a slot for a new task
    print("\nStep 1: Find next available slot for 25-minute task")
    slot_result = scheduler.find_next_available_slot(25)
    print(f"  {slot_result['recommendation']}")

    # Calculate scores for all tasks including the new one
    print("\nStep 2: Calculate priority scores for comprehensive planning")
    all_tasks = existing_tasks + [
        Task("New: Evening Groom", 25, Priority.MEDIUM, Category.GROOMING, TimeOfDay.EVENING, completed=False, frequency=Frequency.WEEKLY)
    ]
    score_result = scheduler.calculate_schedule_score(all_tasks)

    print(f"  Total tasks to manage: {len(all_tasks)}")
    print(f"  Average importance score: {score_result['average_score']:.2f}")
    print(f"  Overall schedule urgency: {score_result['schedule_urgency']}")
    print(f"  Top priority task: {score_result['highest_priority_tasks'][0] if score_result['highest_priority_tasks'] else 'None'}")

    print("\n✓ Integration test passed!")


if __name__ == "__main__":
    test_find_next_available_slot()
    test_calculate_schedule_score()
    test_integration()
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED!")
    print("=" * 70)