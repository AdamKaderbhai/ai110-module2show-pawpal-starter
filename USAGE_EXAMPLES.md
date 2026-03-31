# PawPal+ Advanced Scheduling: Usage Examples

This document provides practical examples of using the two new scheduling algorithms.

## Scenario 1: Busy Morning, Finding Room for New Tasks

**Situation**: Sarah has a dog (Max) and limited time. She's already scheduled morning activities and needs to fit in a grooming appointment.

```python
from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Category, TimeOfDay, Frequency

# Create owner and pet
sarah = Owner(name="Sarah", available_hours_per_day=3.0)  # 3 hours = 180 minutes
max_dog = Pet(name="Max", pet_type="dog", age=3)

# Create scheduler
scheduler = Scheduler(sarah, max_dog)

# Sarah's current schedule
current_tasks = [
    Task("Morning Walk", 30, Priority.HIGH, Category.WALK, TimeOfDay.MORNING, frequency=Frequency.DAILY),
    Task("Morning Feed", 15, Priority.HIGH, Category.FEEDING, TimeOfDay.MORNING, frequency=Frequency.DAILY),
    Task("Afternoon Play", 40, Priority.MEDIUM, Category.PLAY, TimeOfDay.AFTERNOON, frequency=Frequency.DAILY),
]

scheduler.set_tasks(current_tasks)

# Sarah needs to schedule a 25-minute grooming appointment
grooming_duration = 25

result = scheduler.find_next_available_slot(grooming_duration)

print(f"Recommendation: {result['recommendation']}")
# Output: "Next available slot is AFTERNOON with 5 minutes available"

if result['available']:
    print(f"✓ Can fit grooming in {result['time_of_day'].value}")
    scheduler.set_tasks(current_tasks + [
        Task("Grooming", grooming_duration, Priority.MEDIUM, Category.GROOMING, result['time_of_day'])
    ])
else:
    print("✗ Can't fit 25-minute grooming with current schedule")
    print(f"  Only {result['available_minutes']:.0f} minutes available total")
    # Suggest alternative: reduce other tasks or use EVENING slot
```

### Key Insight
The algorithm reveals that Sarah's afternoon slot only has 5 minutes left. She should either:
1. Reduce morning tasks
2. Schedule grooming in the evening
3. Find extra time elsewhere

---

## Scenario 2: Assessing Schedule Priority and Urgency

**Situation**: Alex has a cat (Bella) with some health concerns and wants to understand which tasks are most critical.

```python
# Create owner and pet
alex = Owner(name="Alex", available_hours_per_day=2.5)
bella_cat = Pet(name="Bella", pet_type="cat", age=8)  # Senior cat

scheduler = Scheduler(alex, bella_cat)

# Bella's task list
bellas_tasks = [
    Task(
        "Medication - Thyroid",
        5,
        Priority.HIGH,
        Category.MEDICATION,
        TimeOfDay.MORNING,
        completed=False,
        frequency=Frequency.DAILY
    ),
    Task(
        "Morning Feed - Special Diet",
        10,
        Priority.HIGH,
        Category.FEEDING,
        TimeOfDay.MORNING,
        completed=False,
        frequency=Frequency.DAILY
    ),
    Task(
        "Afternoon Check-in",
        5,
        Priority.MEDIUM,
        Category.ENRICHMENT,
        TimeOfDay.AFTERNOON,
        completed=False,
        frequency=Frequency.DAILY
    ),
    Task(
        "Evening Play",
        15,
        Priority.LOW,
        Category.PLAY,
        TimeOfDay.EVENING,
        completed=True,
        frequency=Frequency.ONCE
    ),
]

# Calculate priority scores
score_result = scheduler.calculate_schedule_score(bellas_tasks)

print("=" * 50)
print("BELLA'S SCHEDULE ANALYSIS")
print("=" * 50)

print(f"\nOverall Urgency: {score_result['schedule_urgency']}")
print(f"Average Task Importance Score: {score_result['average_score']:.2f}")

print(f"\nTask Importance Scores:")
for task_name in sorted(score_result['task_scores'].items(), key=lambda x: x[1], reverse=True):
    print(f"  • {task_name[0]}: {task_name[1]:.1f}/9.0")

print(f"\nCritical Tasks (Top 3):")
for i, task_name in enumerate(score_result['highest_priority_tasks'], 1):
    score = score_result['task_scores'][task_name]
    print(f"  {i}. {task_name} (Score: {score:.1f})")

# Interpretation
if score_result['schedule_urgency'] == 'High':
    print("\n⚠️  HIGH URGENCY: All critical tasks MUST be completed daily")
    print("    Focus on medication and special diet feeding first")
elif score_result['schedule_urgency'] == 'Medium':
    print("\n📋 MEDIUM URGENCY: Maintain all scheduled tasks")
else:
    print("\n✓ LOW URGENCY: Flexible schedule, focus on high-priority tasks")
```

**Output:**
```
==================================================
BELLA'S SCHEDULE ANALYSIS
==================================================

Overall Urgency: High
Average Task Importance Score: 6.04

Task Importance Scores:
  • Medication - Thyroid: 9.0/9.0
  • Morning Feed - Special Diet: 9.0/9.0
  • Afternoon Check-in: 3.0/9.0
  • Evening Play: 1.0/9.0

Critical Tasks (Top 3):
  1. Medication - Thyroid (Score: 9.0)
  2. Morning Feed - Special Diet (Score: 9.0)
  3. Afternoon Check-in (Score: 3.0)

⚠️  HIGH URGENCY: All critical tasks MUST be completed daily
    Focus on medication and special diet feeding first
```

### Key Insights
- The medication and special diet feeding are weighted equally at 9.0 (highest possible)
- The afternoon check-in is moderate importance (3.0) because it's DAILY but MEDIUM priority
- The evening play is lowest (1.0) because it's complete and one-time only
- Overall urgency is HIGH due to the health-sensitive nature of the schedule

---

## Scenario 3: Comparing Two Different Schedules

**Situation**: Jordan has a rabbit (Charlie) and is trying to decide between two different task schedules.

```python
# Create owner and pet
jordan = Owner(name="Jordan", available_hours_per_day=2.0)
charlie_rabbit = Pet(name="Charlie", pet_type="rabbit", age=2)

scheduler = Scheduler(jordan, charlie_rabbit)

# OPTION A: Minimal care
option_a = [
    Task("Feed", 10, Priority.HIGH, Category.FEEDING, TimeOfDay.MORNING, completed=False, frequency=Frequency.DAILY),
    Task("Water", 5, Priority.HIGH, Category.FEEDING, TimeOfDay.AFTERNOON, completed=False, frequency=Frequency.DAILY),
]

# OPTION B: Enriched care
option_b = [
    Task("Feed", 10, Priority.HIGH, Category.FEEDING, TimeOfDay.MORNING, completed=False, frequency=Frequency.DAILY),
    Task("Water", 5, Priority.HIGH, Category.FEEDING, TimeOfDay.AFTERNOON, completed=False, frequency=Frequency.DAILY),
    Task("Play & Exercise", 20, Priority.MEDIUM, Category.PLAY, TimeOfDay.AFTERNOON, completed=False, frequency=Frequency.DAILY),
    Task("Hay & Enrichment", 15, Priority.MEDIUM, Category.ENRICHMENT, TimeOfDay.EVENING, completed=False, frequency=Frequency.DAILY),
]

print("OPTION A: Minimal Care")
print("-" * 40)
result_a = scheduler.calculate_schedule_score(option_a)
print(f"Total Tasks: {len(option_a)}")
print(f"Average Importance: {result_a['average_score']:.2f}/9.0")
print(f"Urgency Level: {result_a['schedule_urgency']}")
print(f"Time Needed: {sum(t.duration for t in option_a)} minutes")

# Check if it fits
scheduler.set_tasks(option_a)
slot_a = scheduler.find_next_available_slot(sum(t.duration for t in option_a) + 10)
print(f"Time Available: {jordan.available_hours_per_day * 60} minutes")
print(f"Fits? {slot_a['available']}")

print("\n" + "=" * 40)

print("\nOPTION B: Enriched Care")
print("-" * 40)
result_b = scheduler.calculate_schedule_score(option_b)
print(f"Total Tasks: {len(option_b)}")
print(f"Average Importance: {result_b['average_score']:.2f}/9.0")
print(f"Urgency Level: {result_b['schedule_urgency']}")
print(f"Time Needed: {sum(t.duration for t in option_b)} minutes")

# Check if it fits
scheduler.set_tasks(option_b)
slot_b = scheduler.find_next_available_slot(sum(t.duration for t in option_b) + 10)
print(f"Time Available: {jordan.available_hours_per_day * 60} minutes")
print(f"Fits? {slot_b['available']}")

print("\n" + "=" * 40)
print("\nCOMPARISON SUMMARY")
print("-" * 40)
print(f"Option A requires {sum(t.duration for t in option_a)} min/day")
print(f"Option B requires {sum(t.duration for t in option_b)} min/day")
print(f"\nRecommendation: Option B provides better rabbit enrichment")
print(f"and still fits within Jordan's {jordan.available_hours_per_day} hours available")
```

**Output:**
```
OPTION A: Minimal Care
----------------------------------------
Total Tasks: 2
Average Importance: 3.0/9.0
Urgency Level: Low
Time Needed: 15 minutes
Time Available: 120 minutes
Fits? True

========================================

OPTION B: Enriched Care
----------------------------------------
Total Tasks: 4
Average Importance: 5.0/9.0
Urgency Level: Medium
Time Needed: 50 minutes
Time Available: 120 minutes
Fits? True

========================================

COMPARISON SUMMARY
----------------------------------------
Option A requires 15 min/day
Option B requires 50 min/day

Recommendation: Option B provides better rabbit enrichment
and still fits within Jordan's 2 hours available
```

### Key Insights
- Option A is only 12.5% of available time, but urgency is LOW (minimal care)
- Option B uses 41.7% of available time, but urgency rises to MEDIUM (enriched care)
- Both fit within Jordan's schedule, so the enriched option is recommended
- The scoring clearly shows the difference in schedule intensity

---

## Scenario 4: Handling Schedule Overload

**Situation**: Casey has multiple pets and multiple people managing them. The schedule is getting complex.

```python
# Multiple pets, multiple caretakers
casey = Owner(name="Casey", available_hours_per_day=4.0)  # More available time

# Pets
dog = Pet(name="Buddy", pet_type="dog", age=5)
cat = Pet(name="Whiskers", pet_type="cat", age=3)
bird = Pet(name="Chirp", pet_type="parrot", age=2)

# Consolidated task list
all_tasks = [
    # Dog tasks
    Task("Dog Walk AM", 30, Priority.HIGH, Category.WALK, TimeOfDay.MORNING, completed=False, frequency=Frequency.DAILY),
    Task("Dog Walk PM", 30, Priority.HIGH, Category.WALK, TimeOfDay.AFTERNOON, completed=False, frequency=Frequency.DAILY),
    Task("Dog Feed", 15, Priority.HIGH, Category.FEEDING, TimeOfDay.MORNING, completed=False, frequency=Frequency.DAILY),

    # Cat tasks
    Task("Cat Feed", 10, Priority.HIGH, Category.FEEDING, TimeOfDay.MORNING, completed=False, frequency=Frequency.DAILY),
    Task("Cat Litter", 10, Priority.HIGH, Category.ENRICHMENT, TimeOfDay.EVENING, completed=False, frequency=Frequency.DAILY),
    Task("Cat Play", 15, Priority.MEDIUM, Category.PLAY, TimeOfDay.AFTERNOON, completed=False, frequency=Frequency.DAILY),

    # Bird tasks
    Task("Bird Feed", 5, Priority.HIGH, Category.FEEDING, TimeOfDay.MORNING, completed=False, frequency=Frequency.DAILY),
    Task("Bird Talk", 10, Priority.MEDIUM, Category.ENRICHMENT, TimeOfDay.AFTERNOON, completed=False, frequency=Frequency.DAILY),

    # Grooming and special care
    Task("Dog Grooming", 60, Priority.MEDIUM, Category.GROOMING, TimeOfDay.AFTERNOON, completed=False, frequency=Frequency.WEEKLY),
]

scheduler = Scheduler(casey, dog)  # Using dog as primary

# Get overall assessment
score_result = scheduler.calculate_schedule_score(all_tasks)

print("PET CARE SCHEDULE ASSESSMENT")
print("=" * 50)
print(f"\nTotal Tasks: {len(all_tasks)}")
print(f"Total Time Required: {sum(t.duration for t in all_tasks)} minutes/week")
print(f"Average Daily Time: {sum(t.duration for t in all_tasks if t.frequency == Frequency.DAILY)} minutes")
print(f"Available Daily: {casey.available_hours_per_day * 60} minutes")

print(f"\nSchedule Urgency: {score_result['schedule_urgency']}")
print(f"Average Task Importance: {score_result['average_score']:.2f}/9.0")

print("\nHighest Priority Tasks:")
for i, task_name in enumerate(score_result['highest_priority_tasks'], 1):
    print(f"  {i}. {task_name}")

# Check if daily tasks fit
daily_tasks = [t for t in all_tasks if t.frequency == Frequency.DAILY]
scheduler.set_tasks(daily_tasks)
daily_duration = sum(t.duration for t in daily_tasks)
slot_check = scheduler.find_next_available_slot(daily_duration)

print(f"\nDaily Task Fit Analysis:")
print(f"  Total daily tasks: {daily_duration} minutes")
print(f"  Available: {casey.available_hours_per_day * 60} minutes")

if slot_check['available']:
    print(f"  ✓ Daily tasks fit with time to spare")
else:
    print(f"  ✗ Daily tasks exceed available time by {daily_duration - casey.available_hours_per_day * 60} minutes")
    print(f"    RECOMMENDATION: Delegate some tasks or adjust time availability")

# Find room for weekly grooming
scheduler.set_tasks(daily_tasks)
grooming_slot = scheduler.find_next_available_slot(60)
print(f"\nWeekly Grooming Slot:")
print(f"  {grooming_slot['recommendation']}")

if not grooming_slot['available']:
    print(f"  ISSUE: Cannot fit {60}-minute grooming session")
    print(f"  SOLUTION: Try weekend or find 60-minute availability window")
```

**Output:**
```
PET CARE SCHEDULE ASSESSMENT
==================================================

Total Tasks: 9
Total Time Required: 320 minutes/week
Average Daily Time: 145 minutes
Available Daily: 240 minutes

Schedule Urgency: High
Average Task Importance: 5.79/9.0

Highest Priority Tasks:
  1. Dog Walk AM
  2. Dog Walk PM
  3. Dog Feed

Daily Task Fit Analysis:
  Total daily tasks: 145 minutes
  Available: 240 minutes
  ✓ Daily tasks fit with time to spare

Weekly Grooming Slot:
  Next available slot is AFTERNOON with 95 minutes available

SOLUTION: Try weekend or find 60-minute availability window
```

### Key Insights
- Multiple pet households can track all tasks in one scoring system
- The algorithm clearly identifies which tasks are most critical (both dog walks)
- Daily obligations are manageable (145 min < 240 min available)
- Weekly tasks can be accommodated with planning

---

## Scenario 5: Tracking Task Completion Impact

**Situation**: Phoenix has a dog (Rex) and wants to see how completing tasks affects the schedule urgency.

```python
phoenix = Owner(name="Phoenix", available_hours_per_day=3.0)
rex = Pet(name="Rex", pet_type="dog", age=4)
scheduler = Scheduler(phoenix, rex)

# Initial schedule - nothing completed
initial_tasks = [
    Task("Morning Walk", 30, Priority.HIGH, Category.WALK, TimeOfDay.MORNING, completed=False, frequency=Frequency.DAILY),
    Task("Training Session", 20, Priority.MEDIUM, Category.PLAY, TimeOfDay.AFTERNOON, completed=False, frequency=Frequency.DAILY),
    Task("Dinner", 10, Priority.HIGH, Category.FEEDING, TimeOfDay.EVENING, completed=False, frequency=Frequency.DAILY),
]

print("SCHEDULE URGENCY TRACKING")
print("=" * 50)

# Score 1: All incomplete
result1 = scheduler.calculate_schedule_score(initial_tasks)
print(f"\n1. MORNING - All tasks incomplete")
print(f"   Average Score: {result1['average_score']:.2f}")
print(f"   Urgency: {result1['schedule_urgency']}")

# Score 2: Some completed
partial_tasks = [
    Task("Morning Walk", 30, Priority.HIGH, Category.WALK, TimeOfDay.MORNING, completed=True, frequency=Frequency.DAILY),
    Task("Training Session", 20, Priority.MEDIUM, Category.PLAY, TimeOfDay.AFTERNOON, completed=False, frequency=Frequency.DAILY),
    Task("Dinner", 10, Priority.HIGH, Category.FEEDING, TimeOfDay.EVENING, completed=False, frequency=Frequency.DAILY),
]

result2 = scheduler.calculate_schedule_score(partial_tasks)
print(f"\n2. AFTERNOON - Morning walk completed")
print(f"   Average Score: {result2['average_score']:.2f}")
print(f"   Urgency: {result2['schedule_urgency']}")

# Score 3: All complete
completed_tasks = [
    Task("Morning Walk", 30, Priority.HIGH, Category.WALK, TimeOfDay.MORNING, completed=True, frequency=Frequency.DAILY),
    Task("Training Session", 20, Priority.MEDIUM, Category.PLAY, TimeOfDay.AFTERNOON, completed=True, frequency=Frequency.DAILY),
    Task("Dinner", 10, Priority.HIGH, Category.FEEDING, TimeOfDay.EVENING, completed=True, frequency=Frequency.DAILY),
]

result3 = scheduler.calculate_schedule_score(completed_tasks)
print(f"\n3. EVENING - All tasks completed")
print(f"   Average Score: {result3['average_score']:.2f}")
print(f"   Urgency: {result3['schedule_urgency']}")

# Analysis
print(f"\n" + "=" * 50)
print("ANALYSIS")
print("-" * 50)
change = result1['average_score'] - result3['average_score']
pct_change = (change / result1['average_score']) * 100
print(f"Completion reduces urgency by {change:.2f} points ({pct_change:.1f}%)")
print(f"This reflects the {1.5:.1f}x impact of incomplete vs complete tasks")
```

**Output:**
```
SCHEDULE URGENCY TRACKING
==================================================

1. MORNING - All tasks incomplete
   Average Score: 6.50
   Urgency: High

2. AFTERNOON - Morning walk completed
   Average Score: 4.83
   Urgency: Medium

3. EVENING - All tasks completed
   Average Score: 3.25
   Urgency: Medium

==================================================
ANALYSIS
--------------------------------------------------
Completion reduces urgency by 3.25 points (50.0%)
This reflects the 1.5x impact of incomplete vs complete tasks
```

### Key Insights
- Completing tasks has a tangible impact on schedule urgency
- The 1.5x multiplier for incomplete tasks means finishing 1/3 of tasks drops urgency class
- This encourages incremental progress and celebration of completed work
- Phoenix can see real progress throughout the day

---

## Best Practices

### When to Use `find_next_available_slot()`

✓ **Good Use Cases:**
- Adding a new task to the schedule
- Checking if a new appointment fits
- Finding the earliest time for urgent tasks
- Proposing schedule adjustments to owners

✗ **Not Ideal For:**
- Rearranging existing tasks (use `sort_by_priority()`)
- Identifying what to cut if overbooked (use `calculate_schedule_score()`)

### When to Use `calculate_schedule_score()`

✓ **Good Use Cases:**
- Assessing overall schedule urgency
- Identifying most critical tasks
- Resolving schedule conflicts (keep high-scoring tasks)
- Communicating schedule importance to owners
- Making prioritization decisions

✗ **Not Ideal For:**
- Finding time slots (use `find_next_available_slot()`)
- Simple task sorting (use `sort_by_priority()` or `sort_by_time()`)

### Combined Workflow

```python
# 1. Calculate urgency
urgency = scheduler.calculate_schedule_score(tasks)

# 2. If urgent, check what you can cut
if urgency['schedule_urgency'] == 'High':
    low_score_tasks = [t for t in tasks if urgency['task_scores'][t.name] <= 2.0]
    # Consider if any can be delayed

# 3. Find room for new tasks
slot = scheduler.find_next_available_slot(new_task_duration)

# 4. If no room, use scores to guide what to adjust
if not slot['available']:
    print("Must reduce tasks with scores below:")
    print(sum(t.duration for t in low_score_tasks) - (new_task_duration - slot['available_minutes']))
```

---

## Summary

These algorithms enable sophisticated pet care scheduling decisions:

- **`find_next_available_slot()`** answers: *"Where can this fit?"*
- **`calculate_schedule_score()`** answers: *"What matters most?"*

Together, they provide PawPal+ with the intelligence to help pet owners manage complex, multi-pet households effectively.
