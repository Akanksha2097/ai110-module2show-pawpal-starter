from datetime import date, datetime, time

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")


def get_owner() -> Owner:
    """Return the Owner stored in session state, creating it only on the first run."""
    if "owner" not in st.session_state:
        st.session_state.owner = Owner("Jordan")
    return st.session_state.owner


def task_rows(tasks: list) -> list:
    """Convert Task objects into simple dict rows for st.table."""
    return [
        {
            "Time": f"{task.due_time:%Y-%m-%d %H:%M}",
            "Pet": task.pet_name,
            "Task": task.description,
            "Frequency": task.frequency,
            "Status": "Done" if task.completed else "Pending",
        }
        for task in tasks
    ]


def task_key(task: Task) -> int:
    """Return a stable unique number for a task, kept in session state across reruns.

    Tasks have no id of their own, so the UI numbers them the first time it sees them.
    The task is stored alongside its number so its object id can never be reused.
    """
    keys = st.session_state.setdefault("task_keys", {})
    if id(task) not in keys:
        keys[id(task)] = (len(keys) + 1, task)
    return keys[id(task)][0]


def conflict_messages(scheduler: Scheduler) -> list:
    """Describe each exact-datetime conflict between pending tasks."""
    return [
        f"Conflict at {first.due_time:%Y-%m-%d %H:%M}: "
        f"{first.pet_name} - {first.description} and {second.pet_name} - {second.description}"
        for first, second in scheduler.find_conflicts()
    ]


def show_conflicts(scheduler: Scheduler) -> None:
    """Show an st.warning for every conflict."""
    for message in conflict_messages(scheduler):
        st.warning(message)


def handle_complete_task(task: Task) -> None:
    """Button callback: complete a task via the Scheduler and queue messages to show next run."""
    owner = get_owner()
    scheduler = Scheduler(owner)
    messages = st.session_state.setdefault("flash", [])
    before = len(owner.get_all_tasks())
    was_completed = task.completed
    try:
        scheduler.complete_task(task)
    except ValueError as error:
        messages.append(("error", str(error)))
        return
    if was_completed:
        messages.append(("info", f"'{task.description}' for {task.pet_name} was already completed."))
        return
    messages.append(("success", f"Completed '{task.description}' for {task.pet_name}."))
    if len(owner.get_all_tasks()) > before:
        new_task = owner.get_pet(task.pet_name).tasks[-1]
        messages.append(
            ("info", f"Next {new_task.frequency} occurrence scheduled for {new_task.due_time:%Y-%m-%d %H:%M}.")
        )
    messages.extend(("warning", text) for text in conflict_messages(scheduler))


def handle_add_pet(owner: Owner, name: str, species: str, age: int) -> None:
    """Validate the form values, add the pet to the owner, and show feedback."""
    name = name.strip()
    if not name:
        st.error("Please enter a pet name.")
        return
    try:
        owner.add_pet(Pet(name, species, int(age)))
    except ValueError as error:
        st.error(str(error))
        return
    st.success(f"Added {name} the {species}.")


def handle_schedule_task(
    owner: Owner, pet_name: str | None, title: str, due_date: date, due_time: time, frequency: str
) -> None:
    """Validate the form values, add the task to the chosen pet, and show feedback."""
    pet = owner.get_pet(pet_name) if pet_name else None
    if pet is None:
        st.error("Add a pet before scheduling a task.")
        return
    title = title.strip()
    if not title:
        st.error("Please enter a task title.")
        return
    try:
        task = Task(title, datetime.combine(due_date, due_time), frequency, pet.name)
        pet.add_task(task)
    except ValueError as error:
        st.error(str(error))
        return
    st.success(f"Scheduled '{title}' for {pet.name} at {task.due_time:%Y-%m-%d %H:%M}.")
    show_conflicts(Scheduler(owner))


st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+. Add your pets, schedule their care tasks, and see everything in time order.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

owner = get_owner()
scheduler = Scheduler(owner)

st.subheader("Owner and Pets")
owner_name = st.text_input("Owner name", value=owner.name)
if owner_name.strip():
    owner.name = owner_name.strip()

col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    age = st.number_input("Age (years)", min_value=0, max_value=40, value=1)

if st.button("Add pet"):
    handle_add_pet(owner, pet_name, species, age)

if owner.pets:
    st.write(f"{owner.name}'s pets:")
    st.table(
        [
            {"Name": pet.name, "Species": pet.species, "Age": pet.age, "Tasks": len(pet.tasks)}
            for pet in owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.markdown("### Tasks")
st.caption("Schedule a task for one of your pets. Tasks are shown in chronological order.")

pet_names = [pet.name for pet in owner.pets]
selected_pet = st.selectbox("Pet", pet_names) if pet_names else None

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    due_date = st.date_input("Date", value=date.today())
with col3:
    due_time = st.time_input("Time", value=time(8, 0))
with col4:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

if st.button("Schedule Task"):
    handle_schedule_task(owner, selected_pet, task_title, due_date, due_time, frequency)

for kind, message in st.session_state.pop("flash", []):
    getattr(st, kind)(message)

all_tasks = scheduler.get_all_tasks()
if all_tasks:
    st.write("All tasks, including completed ones (earliest first):")
    st.table(task_rows(scheduler.sort_by_time(all_tasks)))

    pending_tasks = scheduler.sort_by_time(scheduler.filter_by_status(False))
    if pending_tasks:
        st.write("Mark a pending task as done:")
    for task in pending_tasks:
        text_col, button_col = st.columns([4, 1])
        with text_col:
            st.write(f"{task.due_time:%Y-%m-%d %H:%M} | {task.pet_name} | {task.description} ({task.frequency})")
        with button_col:
            st.button(
                "Mark done",
                key=f"complete_{task_key(task)}",
                on_click=handle_complete_task,
                args=(task,),
            )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Shows your pending tasks across all pets, earliest first.")

if st.button("Generate schedule"):
    pending = scheduler.filter_by_status(False)
    if pending:
        st.success(f"{len(pending)} pending task(s) scheduled.")
        show_conflicts(scheduler)
        st.table(task_rows(scheduler.sort_by_time(pending)))
    else:
        st.error("Nothing to schedule yet. Add a pet and a pending task first.")
