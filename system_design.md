# PawPal+ System Design

## UML Class Diagram (Final Implementation)

```mermaid
classDiagram
    class Owner {
        - name: str
        - available_hours_per_day: float
        - preferences: dict
        - pets: List[Pet]
        - tasks: List[Task]
        + add_task(task: Task) void
        + remove_task(task_name: str) void
        + get_tasks() List[Task]
        + add_pet(pet: Pet) void
        + remove_pet(pet_name: str) void
    }

    class Pet {
        - name: str
        - pet_type: str
        - age: int
        - special_needs: List[str]
        - tasks: List[Task]
        + add_task(task: Task) void
        + remove_task(task_name: str) void
        + get_tasks() List[Task]
    }

    class Task {
        - name: str
        - duration: float
        - priority: Priority
        - category: Category
        - time_of_day: TimeOfDay
        - completed: bool
        - frequency: Frequency
        - scheduled_date: Optional[date]
        + mark_complete() Optional[Task]
        + mark_incomplete() void
        + create_next_occurrence() Optional[Task]
    }

    class Scheduler {
        - owner: Owner
        - pet: Pet
        - scheduled_tasks: List[Task]
        + schedule_day() List[Task]
        + sort_by_time() List[Task]
        + sort_by_priority() List[Task]
        + filter_by_status(completed: bool) List[Task]
        + filter_by_priority(priority: Priority) List[Task]
        + detect_conflicts() List[str]
        + get_schedule() List[Task]
        + format_schedule() str
    }

    class Priority {
        LOW
        MEDIUM
        HIGH
    }

    class Category {
        WALK
        FEEDING
        GROOMING
        MEDICATION
        ENRICHMENT
        PLAY
        SLEEP
        OTHER
    }

    class TimeOfDay {
        MORNING
        AFTERNOON
        EVENING
        FLEXIBLE
    }

    class Frequency {
        ONCE
        DAILY
        WEEKLY
    }

    Owner "1" --> "*" Pet : owns
    Owner "1" --> "*" Task : creates
    Pet "1" --> "*" Task : has
    Scheduler "1" --> "1" Owner : manages
    Scheduler "1" --> "1" Pet : schedules for
    Scheduler "1" --> "*" Task : organizes
    Task --> Priority : uses
    Task --> Category : categorizes
    Task --> TimeOfDay : prefers
    Task --> Frequency : recurs
```

## Class Descriptions

### Owner
Represents the pet owner who manages pets and tasks.
- Holds owner information and daily time constraints
- Can add/remove/view care tasks

### Pet
Represents a pet with basic information.
- Data holder for pet properties (name, type, age, special needs)

### Task
Represents a care task that needs to be scheduled.
- Contains task metadata (name, duration, priority, category, time preference)

### Scheduler
The core logic component that generates daily schedules.
- Takes owner, pet, and task list as input
- Produces an optimized schedule based on constraints and priorities