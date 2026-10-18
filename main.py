"""Demo script for PawPal+: sorting, filtering, conflict detection and recurring tasks."""

from datetime import datetime

from pawpal_system import Owner, Pet, Scheduler, Task

# Fixed example date so the output is the same every run.
TODAY = (2026, 10, 17)


def at(hour: int, minute: int = 0) -> datetime:
    """Build a datetime on the example date at the given time."""
    return datetime(*TODAY, hour, minute)


def print_tasks(title: str, tasks: list) -> None:
    """Print a list of tasks as a simple table."""
    print(f"\n{title}")
    print("-" * 70)
    print(f"{'Time':<18}{'Pet':<8}{'Task':<22}{'Repeats':<10}{'Status'}")
    print("-" * 70)
    if not tasks:
        print("(no tasks)")
    for task in tasks:
        status = "Done" if task.completed else "Pending"
        print(
            f"{task.due_time:%Y-%m-%d %H:%M}  {task.pet_name:<8}"
            f"{task.description:<22}{task.frequency:<10}{status}"
        )


def print_conflicts(scheduler: Scheduler) -> None:
    """Print a warning for every pair of pending tasks at the exact same time."""
    print("\nConflict check")
    print("-" * 70)
    conflicts = scheduler.find_conflicts()
    if not conflicts:
        print("No conflicts found.")
    for first, second in conflicts:
        print(
            f"WARNING: {first.pet_name} ({first.description}) and "
            f"{second.pet_name} ({second.description}) are both scheduled "
            f"at {first.due_time:%Y-%m-%d %H:%M}."
        )


def main() -> None:
    # 1. Set up the owner and pets.
    owner = Owner("Akanksha")
    mochi = Pet("Mochi", "dog", 3)
    luna = Pet("Luna", "cat", 2)
    owner.add_pet(mochi)
    owner.add_pet(luna)
    scheduler = Scheduler(owner)

    # 2. Add tasks deliberately out of chronological order.
    #    (pet_name is filled in automatically by Pet.add_task.)
    breakfast = Task("Breakfast", at(8, 0), "daily", "")
    mochi.add_task(Task("Evening walk", at(18, 0), "daily", ""))
    luna.add_task(Task("Clean litter box", at(12, 30), "daily", ""))
    mochi.add_task(breakfast)
    luna.add_task(Task("Vet check-up", at(15, 45), "once", ""))
    mochi.add_task(Task("Give medication", at(10, 15), "daily", ""))
    luna.add_task(Task("Wet food", at(8, 0), "daily", ""))  # same time as Mochi's breakfast

    print(f"Owner: {owner.name} | Pets: {', '.join(p.name for p in owner.pets)}")
    print_tasks("Tasks in the order they were added", scheduler.get_all_tasks())

    # 3. Sorting: one chronological schedule across both pets.
    print_tasks("Today's Schedule (sorted by time)", scheduler.sort_by_time(scheduler.get_all_tasks()))

    # 4. Filtering by pet.
    for pet in owner.pets:
        pet_tasks = scheduler.sort_by_time(scheduler.filter_by_pet(pet.name))
        print_tasks(f"{pet.name}'s tasks", pet_tasks)

    # 5. Conflict detection: Mochi's Breakfast and Luna's Wet food are both at 08:00.
    print_conflicts(scheduler)

    # 6. Recurring tasks: complete a daily task through the Scheduler.
    scheduler.complete_task(breakfast)
    breakfast_history = [t for t in mochi.tasks if t.description == "Breakfast"]
    print_tasks(
        "After completing Mochi's daily Breakfast: original and next occurrence",
        scheduler.sort_by_time(breakfast_history),
    )

    # 7. Filtering by status, and a fresh conflict check (the 08:00 clash is resolved).
    print_tasks("Completed tasks", scheduler.sort_by_time(scheduler.filter_by_status(True)))
    print_conflicts(scheduler)

    # 8. Pending-only schedule: done tasks are left out, but they stay in each pet's history.
    print_tasks("Pending Schedule (done tasks excluded)", scheduler.sort_by_time(scheduler.filter_by_status(False)))
    print(f"\nTotal tasks kept (history included): {len(scheduler.get_all_tasks())}")


if __name__ == "__main__":
    main()
