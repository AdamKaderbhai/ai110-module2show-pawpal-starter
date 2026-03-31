import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, Priority, Category, TimeOfDay, save_owner_to_json, load_owner_from_json

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+ Scheduler")

st.markdown(
    """
Welcome to **PawPal+** — your pet care planning assistant!
Plan daily tasks for your pets based on time, priority, and preferences.
"""
)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
# Initialize owner in session state (persists across reruns)
if "owner" not in st.session_state:
    # Load owner data from JSON file if it exists, otherwise create a default owner
    st.session_state.owner = load_owner_from_json("pawpal_data.json")

# Initialize pets list in session state (synced with owner's pets)
if "pets" not in st.session_state:
    st.session_state.pets = st.session_state.owner.pets

# Initialize selected pet for scheduling
if "selected_pet" not in st.session_state:
    st.session_state.selected_pet = None

# Initialize scheduled tasks
if "scheduled_tasks" not in st.session_state:
    st.session_state.scheduled_tasks = None


# ============================================================================
# SECTION 1: OWNER INFORMATION
# ============================================================================
st.divider()
st.header("1️⃣ Owner Information")

col1, col2 = st.columns(2)

with col1:
    owner_name = st.text_input(
        "Owner Name",
        value=st.session_state.owner.name,
        help="Your name"
    )

with col2:
    available_hours = st.number_input(
        "Available Hours Per Day",
        min_value=0.5,
        max_value=24.0,
        value=st.session_state.owner.available_hours_per_day,
        step=0.5,
        help="How many hours can you dedicate to pet care daily?"
    )

# Update owner info
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Update Owner Info", key="update_owner"):
        st.session_state.owner.name = owner_name
        st.session_state.owner.available_hours_per_day = available_hours
        st.success("✅ Owner information updated!")

with col2:
    if st.button("Save Progress", key="save_progress"):
        save_owner_to_json(st.session_state.owner, "pawpal_data.json")
        st.success("✅ Progress saved to pawpal_data.json!")

with col3:
    if st.button("Load Data", key="load_data"):
        st.session_state.owner = load_owner_from_json("pawpal_data.json")
        st.session_state.pets = st.session_state.owner.pets
        st.success("✅ Data reloaded from pawpal_data.json!")
        st.rerun()

with col4:
    st.caption("Data persistence controls")


# ============================================================================
# SECTION 2: MANAGE PETS
# ============================================================================
st.divider()
st.header("2️⃣ Manage Pets")

tab1, tab2 = st.tabs(["Add Pet", "View Pets"])

with tab1:
    st.subheader("Add a New Pet")
    col1, col2, col3 = st.columns(3)

    with col1:
        pet_name = st.text_input("Pet Name", value="", key="pet_name_input")

    with col2:
        pet_type = st.selectbox(
            "Pet Type",
            ["Dog", "Cat", "Rabbit", "Bird", "Other"],
            key="pet_type_select"
        )

    with col3:
        pet_age = st.number_input(
            "Pet Age (years)",
            min_value=0,
            max_value=30,
            value=1,
            key="pet_age_input"
        )

    special_needs = st.text_area(
        "Special Needs (comma-separated)",
        placeholder="e.g., gluten-free diet, daily medication",
        key="special_needs_input"
    )

    if st.button("Add Pet", key="add_pet_button"):
        if pet_name.strip():
            # Parse special needs
            needs = [need.strip() for need in special_needs.split(",")] if special_needs.strip() else []

            # Create pet and add to owner
            new_pet = Pet(
                name=pet_name,
                pet_type=pet_type,
                age=pet_age,
                special_needs=needs
            )
            st.session_state.owner.add_pet(new_pet)
            st.session_state.pets.append(new_pet)
            st.success(f"✅ {pet_name} has been added!")
            st.rerun()
        else:
            st.error("Please enter a pet name.")

with tab2:
    st.subheader("Your Pets")
    if st.session_state.pets:
        for pet in st.session_state.pets:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{pet.name}** - {pet.pet_type}, {pet.age} years old")
                    if pet.special_needs:
                        st.caption(f"Special needs: {', '.join(pet.special_needs)}")
                    st.caption(f"Tasks: {len(pet.get_tasks())}")

                with col2:
                    if st.button("Remove", key=f"remove_pet_{pet.name}"):
                        st.session_state.owner.remove_pet(pet.name)
                        st.session_state.pets.remove(pet)
                        st.rerun()
    else:
        st.info("No pets added yet. Add a pet above!")


# ============================================================================
# SECTION 3: MANAGE TASKS
# ============================================================================
st.divider()
st.header("3️⃣ Manage Tasks")

if not st.session_state.pets:
    st.warning("⚠️ Please add a pet first before creating tasks.")
else:
    tab1, tab2 = st.tabs(["Add Task", "View Tasks"])

    with tab1:
        st.subheader("Add a Task")

        # Select which pet this task is for
        pet_names = [pet.name for pet in st.session_state.pets]
        selected_pet_name = st.selectbox(
            "Which pet needs this task?",
            pet_names,
            key="task_pet_select"
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            task_name = st.text_input("Task Name", value="", key="task_name_input")

        with col2:
            duration = st.number_input(
                "Duration (minutes)",
                min_value=1,
                max_value=240,
                value=20,
                key="task_duration_input"
            )

        with col3:
            priority = st.selectbox(
                "Priority",
                ["LOW", "MEDIUM", "HIGH"],
                key="task_priority_select"
            )

        col1, col2 = st.columns(2)

        with col1:
            category = st.selectbox(
                "Category",
                ["WALK", "FEEDING", "GROOMING", "MEDICATION", "ENRICHMENT", "PLAY", "SLEEP", "OTHER"],
                key="task_category_select"
            )

        with col2:
            time_of_day = st.selectbox(
                "Preferred Time",
                ["MORNING", "AFTERNOON", "EVENING", "FLEXIBLE"],
                key="task_time_select"
            )

        if st.button("Add Task", key="add_task_button"):
            if task_name.strip():
                # Find the selected pet
                selected_pet = next((p for p in st.session_state.pets if p.name == selected_pet_name), None)

                if selected_pet:
                    # Create task with correct enum values
                    new_task = Task(
                        name=task_name,
                        duration=float(duration),
                        priority=Priority[priority],
                        category=Category[category],
                        time_of_day=TimeOfDay[time_of_day]
                    )

                    # Add to pet and owner
                    selected_pet.add_task(new_task)
                    st.success(f"✅ Task '{task_name}' added to {selected_pet_name}!")
                    st.rerun()
            else:
                st.error("Please enter a task name.")

    with tab2:
        st.subheader("View Tasks")

        # Emoji mappings
        priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
        category_emoji = {
            "walk": "🚶", "feeding": "🍖", "grooming": "✂️", "medication": "💊",
            "enrichment": "🎾", "play": "🎮", "sleep": "😴", "other": "📋"
        }

        for pet in st.session_state.pets:
            with st.container(border=True):
                col_pet_name, col_pet_info = st.columns([2, 1])
                with col_pet_name:
                    st.write(f"**🐾 {pet.name}'s Tasks**")
                with col_pet_info:
                    st.caption(f"{pet.pet_type} • {pet.age}y old")

                tasks = pet.get_tasks()
                if tasks:
                    for task in tasks:
                        col1, col2, col3, col4, col5 = st.columns([2, 1.2, 1, 1, 0.8])

                        with col1:
                            priority_icon = priority_emoji.get(task.priority.name, "")
                            category_icon = category_emoji.get(task.category.value, "")
                            st.write(f"{category_icon} **{task.name}**")

                        with col2:
                            st.caption(f"{priority_icon} {task.priority.name}")

                        with col3:
                            st.caption(f"⏱️ {int(task.duration)} min")

                        with col4:
                            freq = task.frequency.value if hasattr(task, 'frequency') else "once"
                            freq_emoji = "🔄" if freq != "once" else "1️⃣"
                            st.caption(f"{freq_emoji} {freq}")

                        with col5:
                            if st.button("🗑️", key=f"delete_task_{pet.name}_{task.name}", help="Delete task"):
                                pet.remove_task(task.name)
                                st.rerun()
                else:
                    st.caption("📭 No tasks yet")


# ============================================================================
# SECTION 4: GENERATE SCHEDULE
# ============================================================================
st.divider()
st.header("4️⃣ Generate Daily Schedule")

if not st.session_state.pets or all(len(pet.get_tasks()) == 0 for pet in st.session_state.pets):
    st.warning("⚠️ Add at least one pet with tasks to generate a schedule.")
else:
    # Select which pet to schedule for
    pet_names = [pet.name for pet in st.session_state.pets]
    selected_pet_name = st.selectbox(
        "Generate schedule for:",
        pet_names,
        key="schedule_pet_select"
    )

    selected_pet = next((p for p in st.session_state.pets if p.name == selected_pet_name), None)

    if st.button("Generate Schedule", key="generate_schedule_button"):
        if selected_pet and selected_pet.get_tasks():
            # Create scheduler and generate schedule
            scheduler = Scheduler(st.session_state.owner, selected_pet)
            scheduler.schedule_day()
            st.session_state.scheduled_tasks = (scheduler, selected_pet)
            st.success("✅ Schedule generated!")

    # Display the schedule if it exists
    if st.session_state.scheduled_tasks:
        scheduler, pet = st.session_state.scheduled_tasks

        st.subheader(f"📅 Daily Schedule for {pet.name}")

        # ========================================================================
        # CONFLICT DETECTION WARNING
        # ========================================================================
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.warning("⚠️ **Schedule Conflicts Detected!**")
            st.write("The following tasks are scheduled at the same time:")
            for conflict in conflicts:
                st.write(f"• {conflict}")
            st.info("💡 Consider adjusting task times or durations to avoid overlaps.")
        else:
            st.success("✅ No scheduling conflicts detected!")

        # ========================================================================
        # MAIN SCHEDULE DISPLAY WITH PROFESSIONAL FORMATTING
        # ========================================================================
        # Display as table for better visualization
        st.subheader("Schedule Breakdown")

        # Emoji mappings for visual appeal
        priority_emoji = {
            "HIGH": "🔴",
            "MEDIUM": "🟡",
            "LOW": "🟢"
        }

        category_emoji = {
            "walk": "🚶",
            "feeding": "🍖",
            "grooming": "✂️",
            "medication": "💊",
            "enrichment": "🎾",
            "play": "🎮",
            "sleep": "😴",
            "other": "📋"
        }

        time_emoji = {
            "morning": "🌅",
            "afternoon": "☀️",
            "evening": "🌙",
            "flexible": "⏰"
        }

        tasks_data = []
        for i, task in enumerate(scheduler.get_schedule(), 1):
            priority_icon = priority_emoji.get(task.priority.name, "")
            category_icon = category_emoji.get(task.category.value, "")
            time_icon = time_emoji.get(task.time_of_day.value, "")
            status_icon = "✅" if task.completed else "⏳"

            tasks_data.append({
                "#": i,
                "🎯 Task": f"{task.name}",
                "Priority": f"{priority_icon} {task.priority.name}",
                "📂 Category": f"{category_icon} {task.category.value.title()}",
                "⏱️ Time": f"{time_icon} {task.time_of_day.value.title()}",
                "Duration": f"{int(task.duration)} min",
                "Status": f"{status_icon} {'Done' if task.completed else 'Pending'}"
            })

        st.dataframe(tasks_data, use_container_width=True, hide_index=True)

        # ========================================================================
        # ADVANCED FILTERING AND SORTING
        # ========================================================================
        st.subheader("🔍 Filter & Sort Options")

        col1, col2 = st.columns(2)

        with col1:
            filter_option = st.radio(
                "Filter tasks by:",
                ["All Tasks", "Completed Only", "Pending Only", "High Priority Only"],
                key="filter_radio"
            )

        # Apply filtering
        if filter_option == "Completed Only":
            filtered_tasks = scheduler.filter_by_status(completed=True)
            filter_label = "Completed Tasks"
        elif filter_option == "Pending Only":
            filtered_tasks = scheduler.filter_by_status(completed=False)
            filter_label = "Pending Tasks"
        elif filter_option == "High Priority Only":
            filtered_tasks = scheduler.filter_by_priority(Priority.HIGH)
            filter_label = "High Priority Tasks"
        else:
            filtered_tasks = scheduler.get_schedule()
            filter_label = "All Tasks"

        with col2:
            sort_option = st.radio(
                "Sort tasks by:",
                ["Default (Priority → Time)", "Time of Day", "Priority"],
                key="sort_radio"
            )

        # Apply sorting
        if sort_option == "Time of Day":
            sorted_tasks = scheduler.sort_by_time()
            sort_label = "(sorted by time)"
        elif sort_option == "Priority":
            sorted_tasks = scheduler.sort_by_priority()
            sort_label = "(sorted by priority)"
        else:
            sorted_tasks = scheduler.get_schedule()
            sort_label = ""

        # Display filtered & sorted results
        st.subheader(f"{filter_label} {sort_label}")

        if filtered_tasks:
            # Reuse emoji mappings from schedule display
            priority_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}
            time_emoji = {"morning": "🌅", "afternoon": "☀️", "evening": "🌙", "flexible": "⏰"}

            filtered_data = []
            for task in filtered_tasks:
                priority_icon = priority_emoji.get(task.priority.name, "")
                time_icon = time_emoji.get(task.time_of_day.value, "")
                status_icon = "✅" if task.completed else "⏳"

                filtered_data.append({
                    "🎯 Task": task.name,
                    "Priority": f"{priority_icon} {task.priority.name}",
                    "⏱️ Time": f"{time_icon} {task.time_of_day.value.title()}",
                    "Duration": f"{int(task.duration)} min",
                    "Status": f"{status_icon} {'Done' if task.completed else 'Pending'}"
                })
            st.dataframe(filtered_data, use_container_width=True, hide_index=True)
        else:
            st.info(f"No tasks match the filter '{filter_label}'")

        # ========================================================================
        # SUMMARY STATISTICS
        # ========================================================================
        st.subheader("📊 Schedule Summary")

        col1, col2, col3 = st.columns(3)

        total_duration = sum(task.duration for task in scheduler.get_schedule())
        available_minutes = st.session_state.owner.available_hours_per_day * 60
        completed_count = len(scheduler.filter_by_status(completed=True))
        pending_count = len(scheduler.filter_by_status(completed=False))

        with col1:
            st.metric("Total Duration", f"{int(total_duration)} min")

        with col2:
            st.metric("Available Time", f"{int(available_minutes)} min")

        with col3:
            if total_duration <= available_minutes:
                st.metric("Status", "✅ Fits")
            else:
                st.metric("Status", "❌ Exceeds")

        # Task breakdown
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Completed Tasks", completed_count)

        with col2:
            st.metric("Pending Tasks", pending_count)


# ============================================================================
# FOOTER
# ============================================================================
st.divider()
st.caption("🐾 PawPal+ — Making pet care planning simple and smart!")
