# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🧱 Phase 2: Core System (CLI)

The core logic lives in [pawpal_system.py](pawpal_system.py) and follows the UML in [diagrams/uml_draft.mmd](diagrams/uml_draft.mmd). The Streamlit UI (`app.py`) is not connected to it yet.

### The four classes

| Class | Role | Key methods |
|-------|------|-------------|
| `Task` (dataclass) | One care task: `description`, `due_time`, `frequency` (`once`, `daily` or `weekly`), `pet_name`, `completed`. The frequency is validated when the task is created. | `mark_complete()`, `next_occurrence()` |
| `Pet` (dataclass) | A pet (`name`, `species`, `age`) that owns a list of tasks. | `add_task()`, `remove_task()`, `get_pending_tasks()` |
| `Owner` | A person who owns pets. Pet names must be unique. | `add_pet()`, `remove_pet()`, `get_pet()`, `get_all_tasks()` |
| `Scheduler` | Reads an owner's tasks to sort and filter them. | `get_all_tasks()`, `sort_by_time()`, `filter_by_pet()`, `filter_by_status()` |

### How they relate

- An `Owner` has zero or more `Pet`s, and a `Pet` has zero or more `Task`s (composition).
- A `Scheduler` holds one `Owner` and reaches every task through it, so it can see tasks across all pets.
- `Pet.add_task()` sets `task.pet_name` to the pet's name, so a task always names the pet that holds it.
- `Task.next_occurrence()` returns a new task one day or one week later and leaves the original unchanged. It returns `None` for `once` tasks.

### Run the CLI demo

```bash
python main.py
```

[main.py](main.py) creates the owner Akanksha with Mochi (dog) and Luna (cat), adds five tasks out of chronological order on a fixed date (2026-10-17), and prints them sorted and filtered.

## 🖥️ Sample Output

Actual output of `python main.py`:

```
Owner: Akanksha | Pets: Mochi, Luna

Tasks in the order they were added
----------------------------------------------------------
Time    Pet       Task                    Status
----------------------------------------------------------
18:00   Mochi     Evening walk            Pending
08:00   Mochi     Breakfast               Done
10:15   Mochi     Give medication         Pending
12:30   Luna      Clean litter box        Done
15:45   Luna      Vet check-up            Pending

Today's Schedule (2026-10-17)
----------------------------------------------------------
Time    Pet       Task                    Status
----------------------------------------------------------
08:00   Mochi     Breakfast               Done
10:15   Mochi     Give medication         Pending
12:30   Luna      Clean litter box        Done
15:45   Luna      Vet check-up            Pending
18:00   Mochi     Evening walk            Pending

Mochi's tasks
----------------------------------------------------------
Time    Pet       Task                    Status
----------------------------------------------------------
08:00   Mochi     Breakfast               Done
10:15   Mochi     Give medication         Pending
18:00   Mochi     Evening walk            Pending

Luna's tasks
----------------------------------------------------------
Time    Pet       Task                    Status
----------------------------------------------------------
12:30   Luna      Clean litter box        Done
15:45   Luna      Vet check-up            Pending

Pending tasks
----------------------------------------------------------
Time    Pet       Task                    Status
----------------------------------------------------------
10:15   Mochi     Give medication         Pending
15:45   Luna      Vet check-up            Pending
18:00   Mochi     Evening walk            Pending

Completed tasks
----------------------------------------------------------
Time    Pet       Task                    Status
----------------------------------------------------------
08:00   Mochi     Breakfast               Done
12:30   Luna      Clean litter box        Done
```

## 🧪 Testing PawPal+

```bash
python -m pytest
```

Actual output (add `-v` to list each test by name):

```
============================= test session starts ==============================
platform darwin -- Python 3.13.15, pytest-9.1.1, pluggy-1.7.0
rootdir: /Users/akanksha/Downloads/CodePath/ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 6 items

tests/test_pawpal.py ......                                              [100%]

============================== 6 passed in 0.01s ===============================
```

The six tests are in [tests/test_pawpal.py](tests/test_pawpal.py). Each one builds its own data on the fixed date 2026-10-17:

| Test | What it checks |
|------|----------------|
| `test_task_completion` | A new task is not completed, and `mark_complete()` sets `completed` to `True`. |
| `test_add_task` | `Pet.add_task()` adds the task to the pet and sets `task.pet_name` to the pet's name. |
| `test_sort_by_time` | `Scheduler.sort_by_time()` orders tasks from two pets chronologically and does not change the input list. |
| `test_filter_by_pet` | `Scheduler.filter_by_pet()` returns only that pet's tasks, and an empty list for an unknown pet. |
| `test_filter_by_status` | `Scheduler.filter_by_status()` separates completed and pending tasks across both pets. |
| `test_owner_get_all_tasks` | `Owner.get_all_tasks()` collects tasks from every pet and returns a copy, so changing it leaves the pets' lists intact. |

## 📐 Smarter Scheduling

Status after Phase 2:

| Feature | Method(s) | Status |
|---------|-----------|--------|
| Task sorting | `Scheduler.sort_by_time()` | Implemented, sorts by due time |
| Filtering | `Scheduler.filter_by_pet()`, `Scheduler.filter_by_status()` | Implemented, works across multiple pets |
| Conflict handling | `Scheduler.find_conflicts()` | **Not yet implemented** (stub, planned for Phase 4) |
| Recurring tasks | `Task.next_occurrence()` | Task-level logic implemented. **Scheduler-managed recurrence (`Scheduler.complete_task()`) is not yet implemented** (stub, planned for Phase 4). |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
