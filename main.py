"""Demo script for the PawPal+ core classes (Owner, Pet, Task, Scheduler)."""

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
    print("-" * 58)
    print(f"{'Time':<8}{'Pet':<10}{'Task':<24}{'Status'}")
    print("-" * 58)
    if not tasks:
        print("(no tasks)")
    for task in tasks:
        status = "Done" if task.completed else "Pending"
        print(f"{task.due_time:%H:%M}   {task.pet_name:<10}{task.description:<24}{status}")


def main() -> None:
    # 1. Set up the owner and pets.
    owner = Owner("Akanksha")
    mochi = Pet("Mochi", "dog", 3)
    luna = Pet("Luna", "cat", 2)
    owner.add_pet(mochi)
    owner.add_pet(luna)

    # 2. Add tasks deliberately out of chronological order.
    #    (pet_name is filled in automatically by Pet.add_task.)
    mochi.add_task(Task("Evening walk", at(18, 0), "daily", ""))
    luna.add_task(Task("Clean litter box", at(12, 30), "daily", ""))
    mochi.add_task(Task("Breakfast", at(8, 0), "daily", ""))
    luna.add_task(Task("Vet check-up", at(15, 45), "once", ""))
    mochi.add_task(Task("Give medication", at(10, 15), "daily", ""))

    # Mark a couple of tasks as done so the status column has variety.
    breakfast = mochi.tasks[1]
    breakfast.mark_complete()
    luna.tasks[0].mark_complete()  # Clean litter box

    scheduler = Scheduler(owner)

    # 3. Show the tasks as they were added, then sorted by time.
    print(f"Owner: {owner.name} | Pets: {', '.join(p.name for p in owner.pets)}")
    print_tasks("Tasks in the order they were added", scheduler.get_all_tasks())

    sorted_tasks = scheduler.sort_by_time(scheduler.get_all_tasks())
    print_tasks("Today's Schedule (2026-10-17)", sorted_tasks)

    # 4. Filter by pet (then sort each result).
    for pet in owner.pets:
        pet_tasks = scheduler.sort_by_time(scheduler.filter_by_pet(pet.name))
        print_tasks(f"{pet.name}'s tasks", pet_tasks)

    # 5. Filter by status.
    print_tasks("Pending tasks", scheduler.sort_by_time(scheduler.filter_by_status(False)))
    print_tasks("Completed tasks", scheduler.sort_by_time(scheduler.filter_by_status(True)))


if __name__ == "__main__":
    main()
