"""PawPal+ core system: class skeletons for Owner, Pet, Task, and Scheduler."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from itertools import combinations
from typing import Dict, List, Optional, Tuple

VALID_FREQUENCIES = ("once", "daily", "weekly")


@dataclass
class Task:
    """A single pet care task."""

    description: str
    due_time: datetime
    frequency: str
    pet_name: str
    completed: bool = False

    def __post_init__(self) -> None:
        """Normalize and validate the frequency value."""
        self.frequency = self.frequency.strip().lower()
        if self.frequency not in VALID_FREQUENCIES:
            raise ValueError(
                f"Invalid frequency {self.frequency!r}; "
                f"expected one of {VALID_FREQUENCIES}"
            )

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> Optional[Task]:
        """Return a new, incomplete Task one day/week later, or None if it is a one-time task."""
        if self.frequency == "daily":
            delta = timedelta(days=1)
        elif self.frequency == "weekly":
            delta = timedelta(weeks=1)
        else:
            return None
        return replace(self, due_time=self.due_time + delta, completed=False)


@dataclass
class Pet:
    """A pet and its care tasks."""

    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet and sync the task's pet_name to this pet."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet (matched by identity); raise ValueError if absent."""
        for i, existing in enumerate(self.tasks):
            if existing is task:
                del self.tasks[i]
                return
        raise ValueError(f"Task {task.description!r} not found for pet {self.name!r}")

    def get_pending_tasks(self) -> List[Task]:
        """Return this pet's incomplete tasks."""
        return [t for t in self.tasks if not t.completed]


class Owner:
    """A pet owner who has zero or more pets."""

    def __init__(self, name: str, pets: List[Pet] | None = None) -> None:
        """Create an owner with a name and an optional list of pets."""
        self.name: str = name
        self.pets: List[Pet] = []
        for pet in pets or []:
            self.add_pet(pet)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner; raise ValueError if the name is already taken."""
        if self.get_pet(pet.name) is not None:
            raise ValueError(f"Pet named {pet.name!r} already exists for {self.name!r}")
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove the pet with the given name; raise ValueError if absent."""
        pet = self.get_pet(pet_name)
        if pet is None:
            raise ValueError(f"No pet named {pet_name!r} found for {self.name!r}")
        self.pets.remove(pet)

    def get_pet(self, pet_name: str) -> Optional[Pet]:
        """Return the pet with the given name, or None if there is no match."""
        for pet in self.pets:
            if pet.name == pet_name:
                return pet
        return None

    def get_all_tasks(self) -> List[Task]:
        """Return a new list of all tasks across all pets, leaving each pet's list untouched."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Reads an owner's tasks to sort, filter, and check for conflicts."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler bound to an owner."""
        self.owner: Owner = owner

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks for the owner by delegating to the Owner."""
        return self.owner.get_all_tasks()

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return a new list of the given tasks sorted by due time, leaving the input unchanged."""
        return sorted(tasks, key=lambda task: task.due_time)

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        """Return tasks belonging to the named pet (empty list if the pet is unknown)."""
        pet = self.owner.get_pet(pet_name)
        return list(pet.tasks) if pet is not None else []

    def filter_by_status(self, completed: bool) -> List[Task]:
        """Return tasks across all pets matching the given completion status."""
        return [task for task in self.get_all_tasks() if task.completed == completed]

    def find_conflicts(self) -> List[Tuple[Task, Task]]:
        """Return every unique pair of pending tasks that share the exact same due_time."""
        by_time: Dict[datetime, List[Task]] = {}
        for task in self.get_all_tasks():
            if not task.completed:
                by_time.setdefault(task.due_time, []).append(task)
        conflicts: List[Tuple[Task, Task]] = []
        for group in by_time.values():
            conflicts.extend(combinations(group, 2))
        return conflicts

    def complete_task(self, task: Task) -> None:
        """Complete a task this owner's pet holds and add its next daily/weekly occurrence.

        Raises ValueError if the task isn't owned by this scheduler's owner.
        Completing an already-completed task does nothing, so it never adds a duplicate.
        """
        owning_pet = next(
            (pet for pet in self.owner.pets if any(t is task for t in pet.tasks)), None
        )
        if owning_pet is None:
            raise ValueError(f"Task {task.description!r} does not belong to {self.owner.name!r}")
        if task.completed:
            return
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is not None:
            owning_pet.add_task(next_task)
