# PawPal+ (Module 2 Project)

**PawPal+** is a pet care planner for a busy pet owner. It keeps track of care tasks (walks, feeding, medication, grooming and so on) for several pets, shows them in one chronological schedule, warns about tasks booked at the same moment, and creates the next occurrence of daily and weekly tasks when you finish one.

It has two front ends on the same core classes: a Streamlit app (`app.py`) and a command-line demo (`main.py`).

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

## Features

- Add an owner and any number of pets (pet names are unique per owner).
- Schedule a task for a pet with a date, time and frequency (`once`, `daily` or `weekly`).
- See every task, completed ones included, in chronological order across all pets.
- Mark a pending task done. Daily and weekly tasks get a new pending task one day or one week later, and the finished one stays as history.
- Get a warning when two pending tasks have exactly the same date and time, whether they belong to the same pet or different pets.
- Generate a pending-only schedule that leaves out finished tasks.

## Setup and run

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

```bash
streamlit run app.py    # the Streamlit app
python main.py          # the command-line demo
python -m pytest -v     # the automated tests
```

## System design

The design is in [diagrams/uml_final.mmd](diagrams/uml_final.mmd) (the original plan is [diagrams/uml_draft.mmd](diagrams/uml_draft.mmd)). The code is in [pawpal_system.py](pawpal_system.py).

### Object-oriented design

| Class | Responsibility | Methods |
|-------|----------------|---------|
| `Task` (dataclass) | One care task: `description`, `due_time`, `frequency`, `pet_name`, `completed`. Validates and normalizes `frequency` when it is created. | `mark_complete()`, `next_occurrence()` |
| `Pet` (dataclass) | A pet (`name`, `species`, `age`) that owns its list of tasks. | `add_task()`, `remove_task()`, `get_pending_tasks()` |
| `Owner` | A person who owns pets. Rejects duplicate pet names. | `add_pet()`, `remove_pet()`, `get_pet()`, `get_all_tasks()` |
| `Scheduler` | Works across all of an owner's pets: sorting, filtering, conflict detection and task completion. | `get_all_tasks()`, `sort_by_time()`, `filter_by_pet()`, `filter_by_status()`, `find_conflicts()`, `complete_task()` |

How they relate:

- An `Owner` has zero or more `Pet`s, and a `Pet` has zero or more `Task`s (composition).
- A `Scheduler` holds one `Owner` and reaches every task through it, so it sees all pets without storing its own copy of the data.
- Each class has one job. `Task` knows about itself, `Pet` and `Owner` hold collections, and `Scheduler` holds the logic that spans pets.
- `Pet.add_task()` sets `task.pet_name`, so a task always names the pet that holds it.
- Mutable defaults are safe: `Pet.tasks` uses `field(default_factory=list)`, and `Owner` creates its own list.

Changes from the draft UML: `Owner.get_pet()` and `Task.next_occurrence()` return `Optional` values (`None` for "not found" and for one-time tasks), `find_conflicts()` returns `(Task, Task)` pairs, and the constructors and `Task.__post_init__` were added.

## Algorithms

| Feature | Method | How it works |
|---------|--------|--------------|
| Sorting | `Scheduler.sort_by_time()` | `sorted()` on `due_time`. Returns a new list and leaves the input unchanged. O(n log n). |
| Filtering | `filter_by_pet()`, `filter_by_status()` | Look up the pet by name, or keep tasks whose `completed` flag matches. Both work across all pets. O(n). |
| Conflict detection | `Scheduler.find_conflicts()` | Groups pending tasks in a dictionary keyed by the full `due_time`, then makes every unique pair inside each group with `itertools.combinations`. Grouping is O(n). Producing the pairs costs O(k²) for a group of k tasks at the same time, which is the size of the output. Only exact matches count. |
| Recurrence | `Task.next_occurrence()`, `Scheduler.complete_task()` | `next_occurrence()` uses `dataclasses.replace()` to build a new pending task one day or seven days later and never changes the original. `complete_task()` finds the owning pet by identity (`is`), rejects tasks the owner doesn't have, marks the task done, and adds the next occurrence to the same pet. Completing an already-completed task does nothing, so repeats never add duplicates. |
| Validation | `Task.__post_init__()` | Trims and lowercases the frequency and raises `ValueError` unless it is `once`, `daily` or `weekly`. |

## Streamlit features

Run it with `streamlit run app.py`.

- **Owner and Pets:** edit the owner name, add pets (name, species, age) and see a pets table with task counts. A blank or duplicate name shows `st.error`.
- **Tasks:** pick a pet, title, date, time and frequency, then click **Schedule Task**. A table shows all tasks, completed ones included, earliest first.
- **Mark done:** each pending task has a **Mark done** button that calls `Scheduler.complete_task`. The next occurrence appears right away. Clicking a stale button for an already-completed task shows an info message and creates nothing.
- **Conflict warnings:** `st.warning` names both pets, both tasks and the time. It appears after scheduling a task, after completing a task, and when generating a schedule.
- **Generate schedule:** shows pending tasks only, earliest first.
- **Session state:** the `Owner` is created once in `st.session_state`, so data survives reruns.

## Sample output

Actual output of `python main.py`:

```
Owner: Akanksha | Pets: Mochi, Luna

Tasks in the order they were added
----------------------------------------------------------------------
Time              Pet     Task                  Repeats   Status
----------------------------------------------------------------------
2026-10-17 18:00  Mochi   Evening walk          daily     Pending
2026-10-17 08:00  Mochi   Breakfast             daily     Pending
2026-10-17 10:15  Mochi   Give medication       daily     Pending
2026-10-17 12:30  Luna    Clean litter box      daily     Pending
2026-10-17 15:45  Luna    Vet check-up          once      Pending
2026-10-17 08:00  Luna    Wet food              daily     Pending

Today's Schedule (sorted by time)
----------------------------------------------------------------------
Time              Pet     Task                  Repeats   Status
----------------------------------------------------------------------
2026-10-17 08:00  Mochi   Breakfast             daily     Pending
2026-10-17 08:00  Luna    Wet food              daily     Pending
2026-10-17 10:15  Mochi   Give medication       daily     Pending
2026-10-17 12:30  Luna    Clean litter box      daily     Pending
2026-10-17 15:45  Luna    Vet check-up          once      Pending
2026-10-17 18:00  Mochi   Evening walk          daily     Pending

Mochi's tasks
----------------------------------------------------------------------
Time              Pet     Task                  Repeats   Status
----------------------------------------------------------------------
2026-10-17 08:00  Mochi   Breakfast             daily     Pending
2026-10-17 10:15  Mochi   Give medication       daily     Pending
2026-10-17 18:00  Mochi   Evening walk          daily     Pending

Luna's tasks
----------------------------------------------------------------------
Time              Pet     Task                  Repeats   Status
----------------------------------------------------------------------
2026-10-17 08:00  Luna    Wet food              daily     Pending
2026-10-17 12:30  Luna    Clean litter box      daily     Pending
2026-10-17 15:45  Luna    Vet check-up          once      Pending

Conflict check
----------------------------------------------------------------------
WARNING: Mochi (Breakfast) and Luna (Wet food) are both scheduled at 2026-10-17 08:00.

After completing Mochi's daily Breakfast: original and next occurrence
----------------------------------------------------------------------
Time              Pet     Task                  Repeats   Status
----------------------------------------------------------------------
2026-10-17 08:00  Mochi   Breakfast             daily     Done
2026-10-18 08:00  Mochi   Breakfast             daily     Pending

Completed tasks
----------------------------------------------------------------------
Time              Pet     Task                  Repeats   Status
----------------------------------------------------------------------
2026-10-17 08:00  Mochi   Breakfast             daily     Done

Conflict check
----------------------------------------------------------------------
No conflicts found.

Pending Schedule (done tasks excluded)
----------------------------------------------------------------------
Time              Pet     Task                  Repeats   Status
----------------------------------------------------------------------
2026-10-17 08:00  Luna    Wet food              daily     Pending
2026-10-17 10:15  Mochi   Give medication       daily     Pending
2026-10-17 12:30  Luna    Clean litter box      daily     Pending
2026-10-17 15:45  Luna    Vet check-up          once      Pending
2026-10-17 18:00  Mochi   Evening walk          daily     Pending
2026-10-18 08:00  Mochi   Breakfast             daily     Pending

Total tasks kept (history included): 7
```

## Testing PawPal+

```bash
python -m pytest -v
```

Actual output:

```
============================= test session starts ==============================
platform darwin -- Python 3.13.15, pytest-9.1.1, pluggy-1.7.0 -- /Users/akanksha/Downloads/CodePath/ai110-module2show-pawpal-starter/.venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/akanksha/Downloads/CodePath/ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collecting ... collected 43 items

tests/test_app.py::test_owner_is_created_once_and_persists PASSED        [  2%]
tests/test_app.py::test_invalid_inputs_show_errors PASSED                [  4%]
tests/test_app.py::test_warning_when_adding_conflicting_tasks_across_pets PASSED [  6%]
tests/test_app.py::test_complete_daily_task_keeps_history_and_adds_next PASSED [  9%]
tests/test_app.py::test_complete_once_task_does_not_recur PASSED         [ 11%]
tests/test_app.py::test_button_keys_are_unique_and_stable_across_reruns PASSED [ 13%]
tests/test_app.py::test_completing_task_can_warn_about_new_conflict PASSED [ 16%]
tests/test_app.py::test_generate_schedule_excludes_done_tasks_and_warns_on_conflicts PASSED [ 18%]
tests/test_app.py::test_generate_schedule_with_no_pending_tasks_shows_error PASSED [ 20%]
tests/test_app.py::test_duplicate_pet_name_shows_error_and_keeps_one_pet PASSED [ 23%]
tests/test_app.py::test_weekly_task_recurs_seven_days_later_through_the_ui PASSED [ 25%]
tests/test_app.py::test_repeated_completion_attempts_do_not_duplicate_in_the_ui PASSED [ 27%]
tests/test_pawpal.py::test_task_completion PASSED                        [ 30%]
tests/test_pawpal.py::test_add_task PASSED                               [ 32%]
tests/test_pawpal.py::test_sort_by_time PASSED                           [ 34%]
tests/test_pawpal.py::test_filter_by_pet PASSED                          [ 37%]
tests/test_pawpal.py::test_filter_by_status PASSED                       [ 39%]
tests/test_pawpal.py::test_owner_get_all_tasks PASSED                    [ 41%]
tests/test_pawpal.py::test_complete_daily_task_creates_next_day PASSED   [ 44%]
tests/test_pawpal.py::test_complete_weekly_task_creates_next_week PASSED [ 46%]
tests/test_pawpal.py::test_complete_once_task_does_not_recur PASSED      [ 48%]
tests/test_pawpal.py::test_repeated_completion_does_not_duplicate PASSED [ 51%]
tests/test_pawpal.py::test_complete_task_rejects_foreign_task PASSED     [ 53%]
tests/test_pawpal.py::test_find_conflicts_across_pets PASSED             [ 55%]
tests/test_pawpal.py::test_find_conflicts_same_pet PASSED                [ 58%]
tests/test_pawpal.py::test_find_conflicts_ignores_different_dates_and_times PASSED [ 60%]
tests/test_pawpal.py::test_find_conflicts_ignores_completed_tasks PASSED [ 62%]
tests/test_pawpal.py::test_find_conflicts_three_tasks_gives_all_pairs PASSED [ 65%]
tests/test_pawpal.py::test_find_conflicts_none_and_does_not_mutate PASSED [ 67%]
tests/test_pawpal.py::test_invalid_frequency_raises_value_error[] PASSED [ 69%]
tests/test_pawpal.py::test_invalid_frequency_raises_value_error[   ] PASSED [ 72%]
tests/test_pawpal.py::test_invalid_frequency_raises_value_error[hourly] PASSED [ 74%]
tests/test_pawpal.py::test_invalid_frequency_raises_value_error[dailly] PASSED [ 76%]
tests/test_pawpal.py::test_invalid_frequency_raises_value_error[every day] PASSED [ 79%]
tests/test_pawpal.py::test_invalid_frequency_raises_value_error[monthly] PASSED [ 81%]
tests/test_pawpal.py::test_frequency_is_normalized[ Daily -daily] PASSED [ 83%]
tests/test_pawpal.py::test_frequency_is_normalized[WEEKLY-weekly] PASSED [ 86%]
tests/test_pawpal.py::test_frequency_is_normalized[\tOnce\n-once] PASSED [ 88%]
tests/test_pawpal.py::test_frequency_is_normalized[dAiLy-daily] PASSED   [ 90%]
tests/test_pawpal.py::test_normalized_frequency_still_recurs PASSED      [ 93%]
tests/test_pawpal.py::test_duplicate_pet_name_is_rejected PASSED         [ 95%]
tests/test_pawpal.py::test_duplicate_pet_names_rejected_in_constructor PASSED [ 97%]
tests/test_pawpal.py::test_repeated_completion_attempts_keep_a_single_next_occurrence PASSED [100%]

============================== 43 passed in 1.51s ==============================
```

### What the 43 tests cover

**`tests/test_pawpal.py` (31 tests, core logic):**

- Task completion, and `Pet.add_task()` syncing `pet_name`.
- Sorting across two pets without changing the input, filtering by pet and by status, and `Owner.get_all_tasks()` returning a copy.
- `complete_task()` for daily, weekly and once tasks, repeated completion, and rejecting tasks owned by someone else.
- `find_conflicts()` for same-pet and cross-pet pairs, different dates and times, completed tasks, three simultaneous tasks (three unique pairs), and no conflicts.
- Invalid frequencies raise `ValueError`, and spaces and capitalization are normalized.
- Duplicate pet names are rejected, and repeated completion attempts leave a single next occurrence.

**`tests/test_app.py` (12 tests, Streamlit UI through `streamlit.testing.v1.AppTest`):**

- The owner is created once and persists across reruns.
- Invalid inputs show errors, and a duplicate pet name is rejected.
- Conflict warnings after adding and after completing a task, and in the generated schedule.
- Completing daily, weekly (seven days later, twice in a row) and once tasks, with history kept.
- Unique and stable "Mark done" button keys.
- A stale click on a completed task shows an info message and creates no duplicate.
- Generate schedule excludes finished tasks, and shows an error when nothing is pending.

### Confidence

**4 out of 5.** The core logic is tested directly, including its edge cases, and the Streamlit behavior is tested headlessly. What lowers the score:

- The UI has not been checked in a real browser, only through `AppTest`.
- Test coverage was not measured.
- `Pet.remove_task`, `Owner.remove_pet` and `Owner.get_pet` are not covered by dedicated tests, and `main.py` has no test.
- Conflicts are exact-time matches only, so overlapping tasks that start at different times are not detected.

## Limitations and tradeoffs

- **Exact-time conflicts only.** Tasks have no duration, so a 09:00 task and a 09:01 task do not conflict. This keeps the rule simple and easy to test.
- **No duration, priority or plan explanation.** The scenario mentions constraints, priorities and explaining the plan. The app sorts and filters by time and status but does not rank tasks or explain choices.
- **Pet names are the identifiers.** They are case-sensitive, so "Mochi" and "mochi" count as different pets.
- **Data is in memory only.** Closing the app clears everything.
- **Recurrence happens on completion.** Only completing a task creates the next one, and it is created even if it collides with another task (a warning is shown).

## Demo walkthrough

1. Run `streamlit run app.py`. The page opens with no pets and no tasks.
2. Under **Owner and Pets**, enter a pet name, species and age and click **Add pet**. Add a second pet. Adding the same name again shows an error.
3. Under **Tasks**, choose a pet, enter a title, date, time and frequency, and click **Schedule Task**. The task appears in the table, sorted by time.
4. Schedule a task for the other pet at exactly the same date and time. A warning names both pets, both tasks and the time.
5. Click **Mark done** on a daily task. The original shows as Done and a new pending task appears one day later.
6. Click **Generate schedule**. Only pending tasks are listed, earliest first, with any conflict warnings above the table.
7. For the command-line version, run `python main.py` to see the same features on a fixed date.

**Screenshot or video** *(optional)*: not included.
