"""Automated tests for the PawPal+ core classes."""

from datetime import datetime

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task


def at(hour: int, minute: int = 0) -> datetime:
    """Build a datetime on a fixed example date."""
    return datetime(2026, 10, 17, hour, minute)


@pytest.fixture
def owner():
    """A fresh owner with two pets and four out-of-order tasks (new data per test)."""
    owner = Owner("Akanksha")
    mochi = Pet("Mochi", "dog", 3)
    luna = Pet("Luna", "cat", 2)
    owner.add_pet(mochi)
    owner.add_pet(luna)
    mochi.add_task(Task("Evening walk", at(18, 0), "daily", ""))
    mochi.add_task(Task("Breakfast", at(8, 0), "daily", ""))
    luna.add_task(Task("Vet check-up", at(15, 45), "once", ""))
    luna.add_task(Task("Clean litter box", at(12, 30), "daily", ""))
    return owner


def descriptions(tasks):
    """Return just the task descriptions, for easy comparison."""
    return [task.description for task in tasks]


def test_task_completion():
    task = Task("Walk", at(9), "once", "Mochi")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_add_task():
    pet = Pet("Mochi", "dog", 3)
    task = Task("Walk", at(9), "once", "WrongName")

    pet.add_task(task)

    assert pet.tasks == [task]
    assert task.pet_name == "Mochi"  # synced to the pet's name
    assert len(pet.tasks) == 1


def test_sort_by_time(owner):
    scheduler = Scheduler(owner)
    unsorted_tasks = scheduler.get_all_tasks()
    original_order = list(unsorted_tasks)

    result = scheduler.sort_by_time(unsorted_tasks)

    assert descriptions(result) == [
        "Breakfast",         # Mochi 08:00
        "Clean litter box",  # Luna 12:30
        "Vet check-up",      # Luna 15:45
        "Evening walk",      # Mochi 18:00
    ]
    assert unsorted_tasks == original_order  # input not mutated


def test_filter_by_pet(owner):
    scheduler = Scheduler(owner)

    assert descriptions(scheduler.filter_by_pet("Mochi")) == ["Evening walk", "Breakfast"]
    assert descriptions(scheduler.filter_by_pet("Luna")) == ["Vet check-up", "Clean litter box"]
    assert scheduler.filter_by_pet("Rex") == []


def test_filter_by_status(owner):
    scheduler = Scheduler(owner)
    owner.get_pet("Mochi").tasks[1].mark_complete()  # Breakfast
    owner.get_pet("Luna").tasks[1].mark_complete()   # Clean litter box

    done = scheduler.filter_by_status(True)
    pending = scheduler.filter_by_status(False)

    assert sorted(descriptions(done)) == ["Breakfast", "Clean litter box"]
    assert sorted(descriptions(pending)) == ["Evening walk", "Vet check-up"]


def test_owner_get_all_tasks(owner):
    all_tasks = owner.get_all_tasks()

    assert len(all_tasks) == 4
    assert {task.pet_name for task in all_tasks} == {"Mochi", "Luna"}
    # Returns a new list: changing it must not change the pets' own lists.
    all_tasks.clear()
    assert len(owner.get_pet("Mochi").tasks) == 2
    assert len(owner.get_pet("Luna").tasks) == 2
