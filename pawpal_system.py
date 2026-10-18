"""PawPal+ core system: class skeletons for Owner, Pet, Task, and Scheduler."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@dataclass
class Task:
    """A single pet care task."""

    description: str
    due_time: datetime
    frequency: str
    pet_name: str
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        pass

    def next_occurrence(self) -> Task:
        """Return a new Task for the next occurrence based on frequency."""
        pass


@dataclass
class Pet:
    """A pet and its care tasks."""

    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet."""
        pass

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        pass

    def get_pending_tasks(self) -> List[Task]:
        """Return this pet's incomplete tasks."""
        pass


class Owner:
    """A pet owner who has zero or more pets."""

    def __init__(self, name: str, pets: List[Pet] | None = None) -> None:
        """Create an owner with a name and an optional list of pets."""
        self.name: str = name
        self.pets: List[Pet] = pets if pets is not None else []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        pass

    def remove_pet(self, pet_name: str) -> None:
        """Remove the pet with the given name."""
        pass

    def get_pet(self, pet_name: str) -> Pet:
        """Return the pet with the given name."""
        pass

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks across all of this owner's pets."""
        pass


class Scheduler:
    """Reads an owner's tasks to sort, filter, and check for conflicts."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler bound to an owner."""
        self.owner: Owner = owner

    def get_all_tasks(self) -> List[Task]:
        """Return all tasks for the owner."""
        pass

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return the given tasks sorted by due time."""
        pass

    def filter_by_pet(self, pet_name: str) -> List[Task]:
        """Return tasks belonging to the named pet."""
        pass

    def filter_by_status(self, completed: bool) -> List[Task]:
        """Return tasks matching the given completion status."""
        pass

    def find_conflicts(self) -> list:
        """Return groups of tasks that conflict in time."""
        pass

    def complete_task(self, task: Task) -> None:
        """Mark a task complete and schedule its next occurrence if recurring."""
        pass
