# Advanced Scheduling Algorithms for PawPal+

This document describes the two advanced scheduling algorithms implemented in the `Scheduler` class to go beyond basic sorting.

## Overview

The PawPal+ scheduler now includes two sophisticated algorithms:

1. **Challenge 1: Find Next Available Time Slot** - Analyzes gaps in the schedule
2. **Challenge 3: Weighted Priority Scoring** - Calculates composite importance scores

---

## Challenge 1: `find_next_available_slot(duration_needed: float)`

### Purpose
Finds the next available time slot in a pet owner's schedule that can accommodate a task of a given duration.

### Algorithm Design

#### Core Approach: Time-Based Slot Analysis
The algorithm distributes the owner's available daily time equally across three time periods:
- **MORNING**: 1/3 of available_hours_per_day
- **AFTERNOON**: 1/3 of available_hours_per_day
- **EVENING**: 1/3 of available_hours_per_day
- **FLEXIBLE**: Can use remaining time across all periods

#### Step-by-Step Process

1. **Calculate total available time in minutes**
   ```
   total_available = owner.available_hours_per_day * 60
   base_slot_size = total_available / 3
   ```

2. **Sum task durations for each TimeOfDay**
   - Group all scheduled tasks by their `time_of_day` preference
   - Calculate cumulative duration for each period

3. **Check availability in preference order**
   - Iterate through: MORNING → AFTERNOON → EVENING → FLEXIBLE
   - For each slot, calculate: `available = base_slot_size - time_used`
   - Return the first slot with `available >= duration_needed`

4. **Handle FLEXIBLE tasks**
   - FLEXIBLE tasks can span across unused time in all periods
   - Calculated as: `total_available - sum(all_time_used)`

### Return Value
```python
{
    "available": bool,           # True if slot found
    "time_of_day": TimeOfDay,    # Recommended time slot
    "available_minutes": float,  # Minutes available in that slot
    "recommendation": str        # Human-readable message
}
```

### Example Usage

```python
owner = Owner(name="Sarah", available_hours_per_day=3.0)  # 180 minutes total
pet = Pet(name="Max", pet_type="dog", age=3)
scheduler = Scheduler(owner, pet)

# Add existing tasks
morning_walk = Task("Morning Walk", 40, Priority.HIGH, Category.WALK, TimeOfDay.MORNING)
scheduler.set_tasks([morning_walk])

# Find space for 30-minute task
result = scheduler.find_next_available_slot(30)

if result['available']:
    print(result['recommendation'])  # "Next available slot is AFTERNOON with 60 minutes available"
else:
    print("Schedule is full!")
```

### Trade-offs: Simplicity vs Optimization

#### Simple Approach (Time-based only)
- **Pros**: Easy to understand, single calculation pass
- **Cons**: Doesn't consider task importance, may waste high-priority time slots

#### Complex Approach (Weighted scoring)
- **Pros**: Considers priority, recurrence, and importance
- **Cons**: More computation, harder to explain to users

**Our Choice**: Simple time-based approach for slot finding
- Users expect straightforward scheduling recommendations
- Clear communication is valued in pet care contexts
- The `calculate_schedule_score` method handles complexity separately

### Edge Cases Handled

1. **Empty schedule**: Returns MORNING with full 1/3 of available time
2. **All slots full**: Returns `available=False` with total remaining time
3. **Exact fit**: Returns the slot even if it fills it completely
4. **FLEXIBLE overflow**: Allows tasks to use time across multiple periods

### Future ML Enhancements

```python
# Example: Machine learning improvements

# 1. Learn actual time distribution patterns
def predict_available_time_distribution(owner_history):
    """Use historical data to predict true time availability.

    Instead of equal 1/3 distribution, learn that this owner actually:
    - Has 40% time in morning (early riser)
    - Has 30% time in afternoon
    - Has 30% time in evening
    """
    return learn_from_data(owner_history)

# 2. Predict task duration from category
def predict_task_duration(category, pet_type):
    """Use category and pet type to estimate task duration.

    Example: Walking a large dog typically takes 20-30 minutes
    """
    return estimate_from_patterns(category, pet_type)

# 3. Recommend time based on owner preferences
def recommend_time_of_day(task, owner_preference_profile):
    """Suggest scheduling time based on owner's historical patterns."""
    return get_preferred_slot(task, owner_preference_profile)
```

---

## Challenge 3: `calculate_schedule_score(tasks: List[Task])`

### Purpose
Assigns weighted importance scores to tasks based on multiple factors, providing insight into schedule urgency and priority ranking.

### Scoring Formula

Each task's score is calculated as:

```
base_score = priority_weight + recurrence_bonus + time_alignment_bonus
final_score = base_score * completion_multiplier
```

#### Component Breakdown

1. **Priority Weight** (base value)
   - HIGH = 3 points
   - MEDIUM = 2 points
   - LOW = 1 point

2. **Recurrence Bonus** (0-2 points)
   - DAILY = +2 points (repeats every day)
   - WEEKLY = +1 point (repeats weekly)
   - ONCE = 0 points (one-time task)

3. **Time Alignment Bonus** (0-1 points)
   - +1 point if `time_of_day != FLEXIBLE` (has specific preference)
   - 0 points if FLEXIBLE (can be done anytime)

4. **Completion Status Multiplier**
   - Incomplete tasks: ×1.5 (more urgent)
   - Complete tasks: ×1.0 (less urgent)

### Scoring Examples

```
Example 1: High priority, daily, incomplete, morning-preferred
  base_score = 3 + 2 + 1 = 6
  final_score = 6 * 1.5 = 9.0

Example 2: Medium priority, weekly, incomplete, afternoon-preferred
  base_score = 2 + 1 + 1 = 4
  final_score = 4 * 1.5 = 6.0

Example 3: Low priority, once, complete, flexible
  base_score = 1 + 0 + 0 = 1
  final_score = 1 * 1.0 = 1.0

Example 4: Maximum possible score
  base_score = 3 + 2 + 1 = 6
  final_score = 6 * 1.5 = 9.0
```

### Return Value

```python
{
    "task_scores": Dict[str, float],      # Task name → score mapping
    "average_score": float,               # Average score across all tasks
    "highest_priority_tasks": List[str],  # Top 3 task names by score
    "schedule_urgency": str              # "Low", "Medium", or "High"
}
```

### Schedule Urgency Thresholds

Based on average score across all tasks:

```
average_score >= 3.5    →   "High"   (critical tasks pending)
2.0 <= average < 3.5    →   "Medium" (moderate planning needed)
average < 2.0           →   "Low"    (relaxed schedule)
```

### Example Usage

```python
owner = Owner(name="Alex", available_hours_per_day=4.0)
pet = Pet(name="Bella", pet_type="cat", age=5)
scheduler = Scheduler(owner, pet)

tasks = [
    Task("Morning Walk", 30, Priority.HIGH, Category.WALK,
         TimeOfDay.MORNING, completed=False, frequency=Frequency.DAILY),
    Task("Evening Meal", 15, Priority.HIGH, Category.FEEDING,
         TimeOfDay.EVENING, completed=False, frequency=Frequency.DAILY),
    Task("Play Session", 20, Priority.LOW, Category.PLAY,
         TimeOfDay.FLEXIBLE, completed=True, frequency=Frequency.ONCE),
]

result = scheduler.calculate_schedule_score(tasks)

print(f"Most critical task: {result['highest_priority_tasks'][0]}")
# Output: "Most critical task: Morning Walk"

print(f"Overall urgency: {result['schedule_urgency']}")
# Output: "Overall urgency: High"

print(f"Score breakdown:")
for name, score in result['task_scores'].items():
    print(f"  {name}: {score}")
# Output:
#   Morning Walk: 9.0
#   Evening Meal: 9.0
#   Play Session: 1.0
```

### Algorithm Approaches: Simple vs Complex

#### Simple Approach: Time-Based Only
```python
# Just sort by TimeOfDay
sorted_tasks = sorted(tasks, key=lambda t: time_preference_order[t.time_of_day])
```
- **Pros**: Minimal code, easy to understand
- **Cons**: Loses all priority information, misleading urgency

#### Complex Approach: Weighted Scoring (Implemented)
```python
# Combine multiple factors with weights
score = (priority + recurrence + alignment) * completion_multiplier
```
- **Pros**: Comprehensive view, identifies truly critical work
- **Cons**: Requires careful weight tuning, more computation

**Our Choice**: Weighted scoring
- Pet health often requires HIGH priority tasks to be done regardless of time
- Recurring tasks (daily medication) are more critical than one-off play
- Incomplete tasks are more urgent than completed ones
- All factors matter for good pet care scheduling

### Trade-off Analysis

| Factor | Simple Time-Based | Weighted Scoring |
|--------|------------------|------------------|
| Clarity | Very clear | Requires explanation |
| Sophistication | Too simple | Appropriately complex |
| Computation | O(n) | O(n log n) for sorting |
| Flexibility | Limited | Highly configurable |
| Accuracy | Poor | Excellent |

### Edge Cases Handled

1. **Empty task list**
   ```python
   {
       "task_scores": {},
       "average_score": 0.0,
       "highest_priority_tasks": [],
       "schedule_urgency": "Low"
   }
   ```

2. **Single task**
   - Derives urgency from that one task's score

3. **All complete tasks**
   - Lower overall urgency due to ×1.0 multiplier

4. **Mixed frequencies**
   - Properly weights DAILY > WEEKLY > ONCE

5. **Top 3 tasks with fewer than 3 total**
   - Returns only as many as exist

### Future ML Enhancements

```python
# 1. Dynamic weight learning
def learn_optimal_weights(historical_schedules):
    """Learn weights that best predict owner's actual priority patterns.

    Use gradient descent to optimize:
    score = w1*priority + w2*recurrence + w3*alignment

    Target: minimize (predicted_urgency - actual_owner_urgency)²
    """
    pass

# 2. Clustering owner patterns
def identify_owner_type(owner_schedule_history):
    """Identify if owner is:
    - Morning person (more time early)
    - Night owl (more time late)
    - Balanced (equal distribution)

    Adjust time_alignment_bonus accordingly.
    """
    pass

# 3. Predict task importance from context
def predict_task_importance(task, pet_health_status):
    """Boost score for critical pet health tasks:
    - Medication > routine feeding
    - Vet visit prep > regular play
    """
    pass

# 4. Reinforcement learning
def optimize_schedule_over_time(owner_feedback):
    """Learn from owner's actual choices:
    - Did they skip low-urgency tasks?
    - Did they prioritize different factors?
    - Adjust scoring weights based on patterns.
    """
    pass

# 5. Collaborative filtering
def recommend_schedules_from_similar_owners(owner_demographics):
    """Find owners with similar:
    - Number of pets
    - Pet types
    - Available time
    - Use their successful schedules as templates
    """
    pass
```

---

## Integration: Using Both Algorithms Together

### Workflow Example

```python
# Step 1: Check current schedule's urgency
urgency = scheduler.calculate_schedule_score(pet.tasks)
print(f"Current urgency: {urgency['schedule_urgency']}")

# Step 2: Find available slots for new tasks
if urgency['schedule_urgency'] == 'High':
    # If urgent, look for quick high-priority slots
    slot = scheduler.find_next_available_slot(15)  # 15-minute slots
else:
    # Otherwise, look for longer tasks
    slot = scheduler.find_next_available_slot(45)  # 45-minute sessions

# Step 3: Recommend the new task
if slot['available']:
    print(f"✓ {slot['recommendation']}")
else:
    print(f"⚠ {slot['recommendation']}")
    print("   Consider prioritizing incomplete HIGH tasks")
```

### Decision Tree: When to Use Which Algorithm

```
New task to schedule?
├─ YES: Find available slot with find_next_available_slot()
│       └─ Shows where to fit the task
│
Complete schedule review?
├─ YES: Calculate scores with calculate_schedule_score()
│       └─ Shows what tasks are most critical
│
Conflict detected?
├─ YES: Use scores to resolve (keep higher-scoring tasks)
        └─ Weighted score helps with priority decisions
```

---

## Performance Characteristics

### Time Complexity

| Algorithm | Best Case | Average | Worst Case |
|-----------|-----------|---------|-----------|
| `find_next_available_slot()` | O(n) | O(n) | O(n) |
| `calculate_schedule_score()` | O(n log n) | O(n log n) | O(n log n) |

*n = number of tasks*

### Space Complexity

- `find_next_available_slot()`: O(1) - only stores time_used dict with 4 entries
- `calculate_schedule_score()`: O(n) - stores task_scores dictionary

### Performance Notes

- Both algorithms are efficient for typical pet schedules (5-20 tasks)
- No nested loops used
- Suitable for real-time UI updates

---

## Testing the Implementations

Run the comprehensive test suite:

```bash
python3 test_advanced_scheduling.py
```

Test coverage includes:
- Empty schedules
- Partially filled time slots
- Fully booked schedules
- Exact fit scenarios
- Mixed task priorities and frequencies
- Edge cases (empty lists, single tasks, all complete)
- Integration tests combining both algorithms

All tests demonstrate the algorithms handle edge cases gracefully.

---

## Configuration & Customization

### Adjusting Time Distribution

To change how available time is divided, modify the base_slot_minutes calculation:

```python
# Current: Equal thirds
base_slot_minutes = total_available_minutes / 3

# Alternative: Owner's actual pattern
base_slot_minutes = {
    TimeOfDay.MORNING: total_available_minutes * 0.4,    # 40%
    TimeOfDay.AFTERNOON: total_available_minutes * 0.3,  # 30%
    TimeOfDay.EVENING: total_available_minutes * 0.3,    # 30%
}
```

### Adjusting Scoring Weights

To emphasize different factors, modify the scoring components:

```python
# Current weights
priority_weight = task.priority.value        # 1-3
recurrence_bonus = [0, 1, 2]                # depends on frequency
time_alignment_bonus = 0 or 1                # binary
completion_multiplier = 1.0 or 1.5           # binary

# Alternative: emphasize completion status more
completion_multiplier = 1.0 or 2.0           # higher multiplier for incomplete

# Alternative: emphasize recurrence less
recurrence_bonus = [0, 0.5, 1]              # reduced values
```

### Adjusting Urgency Thresholds

To change what counts as "High" urgency:

```python
# Current thresholds (based on max score of 9.0)
if average_score >= 3.5:
    urgency = "High"

# Alternative: stricter thresholds
if average_score >= 5.0:    # Only truly critical tasks
    urgency = "High"
elif average_score >= 3.0:
    urgency = "Medium"
```

---

## Summary

These two algorithms provide PawPal+ with sophisticated scheduling capabilities:

1. **`find_next_available_slot()`** - Practical, straightforward scheduling
   - Helps find where new tasks fit
   - Easy for users to understand
   - Time-based approach for clarity

2. **`calculate_schedule_score()`** - Deep priority analysis
   - Identifies what tasks matter most
   - Considers all relevant factors
   - Weighted approach for nuance

Together, they enable intelligent, responsive pet care scheduling that adapts to each owner's unique situation.
