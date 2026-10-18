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


# --- Scheduler.complete_task ---


def test_complete_daily_task_creates_next_day(owner):
    scheduler = Scheduler(owner)
    mochi = owner.get_pet("Mochi")
    walk = mochi.tasks[0]  # Evening walk, daily, 2026-10-17 18:00

    scheduler.complete_task(walk)

    assert walk.completed is True
    assert walk.due_time == at(18, 0)  # original history preserved
    assert len(mochi.tasks) == 3
    new_task = mochi.tasks[-1]
    assert new_task is not walk
    assert new_task.description == "Evening walk"
    assert new_task.due_time == datetime(2026, 10, 18, 18, 0)
    assert new_task.completed is False
    assert new_task.pet_name == "Mochi"


def test_complete_weekly_task_creates_next_week():
    owner = Owner("Akanksha")
    luna = Pet("Luna", "cat", 2)
    owner.add_pet(luna)
    bath = Task("Bath", at(10), "weekly", "")
    luna.add_task(bath)

    Scheduler(owner).complete_task(bath)

    assert bath.completed is True
    assert len(luna.tasks) == 2
    assert luna.tasks[1].due_time == datetime(2026, 10, 24, 10, 0)
    assert luna.tasks[1].completed is False


def test_complete_once_task_does_not_recur(owner):
    scheduler = Scheduler(owner)
    luna = owner.get_pet("Luna")
    vet = luna.tasks[0]  # Vet check-up, once

    scheduler.complete_task(vet)

    assert vet.completed is True
    assert len(luna.tasks) == 2  # no new task added


def test_repeated_completion_does_not_duplicate(owner):
    scheduler = Scheduler(owner)
    mochi = owner.get_pet("Mochi")
    walk = mochi.tasks[0]

    scheduler.complete_task(walk)
    scheduler.complete_task(walk)
    scheduler.complete_task(walk)

    assert len(mochi.tasks) == 3  # original two + exactly one recurrence
    assert len(owner.get_all_tasks()) == 5


def test_complete_task_rejects_foreign_task(owner):
    scheduler = Scheduler(owner)
    stranger = Owner("Someone Else")
    rex = Pet("Rex", "dog", 4)
    stranger.add_pet(rex)
    foreign = Task("Evening walk", at(18, 0), "daily", "")  # same fields as Mochi's task
    rex.add_task(foreign)
    unattached = Task("Loose task", at(9), "daily", "Nobody")

    with pytest.raises(ValueError):
        scheduler.complete_task(foreign)
    with pytest.raises(ValueError):
        scheduler.complete_task(unattached)

    assert foreign.completed is False
    assert unattached.completed is False
    assert len(rex.tasks) == 1  # nothing recurred on the other owner's pet
    assert len(owner.get_all_tasks()) == 4


# --- Scheduler.find_conflicts ---


def conflict_owner():
    """Owner with two pets and no tasks, for building conflict scenarios."""
    owner = Owner("Akanksha")
    owner.add_pet(Pet("Mochi", "dog", 3))
    owner.add_pet(Pet("Luna", "cat", 2))
    return owner


def test_find_conflicts_across_pets():
    owner = conflict_owner()
    walk = Task("Walk", at(9), "daily", "")
    feed = Task("Feed", at(9), "daily", "")
    owner.get_pet("Mochi").add_task(walk)
    owner.get_pet("Luna").add_task(feed)

    conflicts = Scheduler(owner).find_conflicts()

    assert len(conflicts) == 1
    assert {id(t) for t in conflicts[0]} == {id(walk), id(feed)}
    assert walk.pet_name != feed.pet_name  # a different-pet conflict


def test_find_conflicts_same_pet():
    owner = conflict_owner()
    mochi = owner.get_pet("Mochi")
    a, b = Task("Walk", at(9), "once", ""), Task("Bath", at(9), "once", "")
    mochi.add_task(a)
    mochi.add_task(b)

    assert Scheduler(owner).find_conflicts() == [(a, b)]


def test_find_conflicts_ignores_different_dates_and_times():
    owner = conflict_owner()
    mochi, luna = owner.get_pet("Mochi"), owner.get_pet("Luna")
    mochi.add_task(Task("Walk", datetime(2026, 10, 17, 9, 0), "once", ""))
    luna.add_task(Task("Feed", datetime(2026, 10, 18, 9, 0), "once", ""))  # next day
    luna.add_task(Task("Play", datetime(2026, 10, 17, 9, 1), "once", ""))  # one minute later

    assert Scheduler(owner).find_conflicts() == []


def test_find_conflicts_ignores_completed_tasks():
    owner = conflict_owner()
    done = Task("Walk", at(9), "once", "")
    pending = Task("Feed", at(9), "once", "")
    owner.get_pet("Mochi").add_task(done)
    owner.get_pet("Luna").add_task(pending)
    done.mark_complete()

    assert Scheduler(owner).find_conflicts() == []


def test_find_conflicts_three_tasks_gives_all_pairs():
    owner = conflict_owner()
    a, b, c = (Task(name, at(9), "once", "") for name in ("Walk", "Feed", "Play"))
    owner.get_pet("Mochi").add_task(a)
    owner.get_pet("Mochi").add_task(b)
    owner.get_pet("Luna").add_task(c)

    conflicts = Scheduler(owner).find_conflicts()

    pairs = {frozenset((id(x), id(y))) for x, y in conflicts}
    assert len(conflicts) == 3  # 3 choose 2, no repeats
    assert pairs == {
        frozenset((id(a), id(b))),
        frozenset((id(a), id(c))),
        frozenset((id(b), id(c))),
    }


def test_find_conflicts_none_and_does_not_mutate(owner):
    scheduler = Scheduler(owner)  # fixture tasks all have different times
    before = [(t.description, t.due_time, t.completed) for t in owner.get_all_tasks()]

    assert scheduler.find_conflicts() == []
    assert [(t.description, t.due_time, t.completed) for t in owner.get_all_tasks()] == before
    assert Scheduler(Owner("Empty")).find_conflicts() == []


# --- Frequency validation, duplicate pets, repeated completion ---


@pytest.mark.parametrize("bad", ["", "   ", "hourly", "dailly", "every day", "monthly"])
def test_invalid_frequency_raises_value_error(bad):
    with pytest.raises(ValueError, match="Invalid frequency"):
        Task("Walk", at(9), bad, "Mochi")


@pytest.mark.parametrize(
    "raw, expected",
    [(" Daily ", "daily"), ("WEEKLY", "weekly"), ("\tOnce\n", "once"), ("dAiLy", "daily")],
)
def test_frequency_is_normalized(raw, expected):
    assert Task("Walk", at(9), raw, "Mochi").frequency == expected


def test_normalized_frequency_still_recurs():
    task = Task("Bath", at(9), "  WEEKLY ", "Mochi")

    assert task.next_occurrence().due_time == datetime(2026, 10, 24, 9, 0)
    assert task.next_occurrence().frequency == "weekly"


def test_duplicate_pet_name_is_rejected():
    owner = Owner("Akanksha")
    mochi = Pet("Mochi", "dog", 3)
    owner.add_pet(mochi)

    with pytest.raises(ValueError, match="already exists"):
        owner.add_pet(Pet("Mochi", "cat", 1))

    assert owner.pets == [mochi]  # the original pet is untouched, nothing added


def test_duplicate_pet_names_rejected_in_constructor():
    with pytest.raises(ValueError, match="already exists"):
        Owner("Akanksha", [Pet("Luna", "cat", 2), Pet("Luna", "dog", 5)])


def test_repeated_completion_attempts_keep_a_single_next_occurrence():
    owner = Owner("Akanksha")
    mochi = Pet("Mochi", "dog", 3)
    owner.add_pet(mochi)
    walk = Task("Walk", at(9), "weekly", "")
    mochi.add_task(walk)
    scheduler = Scheduler(owner)

    for _ in range(5):
        scheduler.complete_task(walk)

    pending = scheduler.filter_by_status(False)
    assert len(mochi.tasks) == 2
    assert [t.due_time for t in pending] == [datetime(2026, 10, 24, 9, 0)]
    assert len(scheduler.filter_by_status(True)) == 1
