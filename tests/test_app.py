"""Streamlit UI tests for app.py, using Streamlit's headless AppTest."""

from datetime import date, time
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).resolve().parent.parent / "app.py")
DAY = date(2026, 10, 17)


@pytest.fixture
def app():
    """A fresh app run with no pets or tasks."""
    at = AppTest.from_file(APP_PATH, default_timeout=20).run()
    assert not at.exception
    return at


def click(at, label):
    next(b for b in at.button if b.label == label).click().run()


def add_pet(at, name, species="dog"):
    next(t for t in at.text_input if t.label == "Pet name").set_value(name)
    next(s for s in at.selectbox if s.label == "Species").set_value(species)
    click(at, "Add pet")


def add_task(at, pet, title, day=DAY, at_time=time(9, 0), frequency="once"):
    next(s for s in at.selectbox if s.label == "Pet").set_value(pet)
    next(t for t in at.text_input if t.label == "Task title").set_value(title)
    next(d for d in at.date_input if d.label == "Date").set_value(day)
    next(t for t in at.time_input if t.label == "Time").set_value(at_time)
    next(s for s in at.selectbox if s.label == "Frequency").set_value(frequency)
    click(at, "Schedule Task")


def done_button(at, description):
    """Return the 'Mark done' button for the pending task with this description."""
    keys = at.session_state.task_keys
    for task in at.session_state.owner.get_all_tasks():
        if task.description == description and not task.completed:
            return at.button(key=f"complete_{keys[id(task)][0]}")
    raise AssertionError(f"no pending task {description!r}")


def table_rows(at):
    """Rows of the first table that lists tasks (the 'all tasks' table)."""
    return next(t.value for t in at.table if "Task" in t.value.columns).to_dict("records")


def test_owner_is_created_once_and_persists(app):
    owner = app.session_state.owner
    add_pet(app, "Mochi")
    add_task(app, "Mochi", "Walk")
    app.run()
    assert app.session_state.owner is owner
    assert len(owner.get_all_tasks()) == 1


def test_invalid_inputs_show_errors(app):
    click(app, "Schedule Task")
    assert [e.value for e in app.error] == ["Add a pet before scheduling a task."]

    add_pet(app, "  ")
    assert "Please enter a pet name." in [e.value for e in app.error]

    add_pet(app, "Mochi")
    add_task(app, "Mochi", "   ")
    assert "Please enter a task title." in [e.value for e in app.error]
    assert app.session_state.owner.get_all_tasks() == []


def test_warning_when_adding_conflicting_tasks_across_pets(app):
    add_pet(app, "Mochi")
    add_pet(app, "Luna", "cat")
    add_task(app, "Mochi", "Walk")
    assert len(app.warning) == 0

    add_task(app, "Luna", "Feed")

    assert len(app.warning) == 1
    text = app.warning[0].value
    for expected in ("Mochi", "Walk", "Luna", "Feed", "2026-10-17 09:00"):
        assert expected in text


def test_complete_daily_task_keeps_history_and_adds_next(app):
    add_pet(app, "Mochi")
    add_task(app, "Mochi", "Walk", frequency="daily")

    done_button(app, "Walk").click().run()

    assert not app.exception
    rows = table_rows(app)
    assert [(r["Time"], r["Task"], r["Status"]) for r in rows] == [
        ("2026-10-17 09:00", "Walk", "Done"),
        ("2026-10-18 09:00", "Walk", "Pending"),
    ]
    assert any("Completed 'Walk'" in s.value for s in app.success)
    assert any("2026-10-18 09:00" in i.value for i in app.info)


def test_complete_once_task_does_not_recur(app):
    add_pet(app, "Mochi")
    add_task(app, "Mochi", "Vet", frequency="once")

    done_button(app, "Vet").click().run()

    assert [(r["Task"], r["Status"]) for r in table_rows(app)] == [("Vet", "Done")]
    assert [b for b in app.button if b.label == "Mark done"] == []


def test_button_keys_are_unique_and_stable_across_reruns(app):
    add_pet(app, "Mochi")
    add_pet(app, "Luna", "cat")
    add_task(app, "Mochi", "Walk", at_time=time(8, 0), frequency="daily")
    add_task(app, "Luna", "Walk", at_time=time(12, 0))  # same description on purpose
    add_task(app, "Mochi", "Play", at_time=time(15, 0))

    def mark_done_keys():
        return [b.key for b in app.button if b.label == "Mark done"]

    keys = mark_done_keys()
    assert len(keys) == 3 and len(set(keys)) == 3
    app.run()
    assert mark_done_keys() == keys

    # Completing the first task must not change the keys of the others.
    app.button(key=keys[0]).click().run()
    remaining = mark_done_keys()
    assert keys[1] in remaining and keys[2] in remaining
    assert keys[0] not in remaining
    assert len(remaining) == 3  # two old tasks + the new daily recurrence
    assert len(set(remaining)) == 3


def test_completing_task_can_warn_about_new_conflict(app):
    add_pet(app, "Mochi")
    add_task(app, "Mochi", "Walk", day=DAY, frequency="daily")
    add_task(app, "Mochi", "Bath", day=date(2026, 10, 18))  # collides with Walk's next day

    done_button(app, "Walk").click().run()

    assert len(app.warning) == 1
    assert "Walk" in app.warning[0].value and "Bath" in app.warning[0].value


def test_generate_schedule_excludes_done_tasks_and_warns_on_conflicts(app):
    add_pet(app, "Mochi")
    add_pet(app, "Luna", "cat")
    add_task(app, "Mochi", "Walk", at_time=time(8, 0))
    add_task(app, "Luna", "Feed", at_time=time(8, 0))
    add_task(app, "Mochi", "Play", at_time=time(15, 0))
    done_button(app, "Play").click().run()

    click(app, "Generate schedule")

    schedule = app.table[-1].value.to_dict("records")
    assert sorted(r["Task"] for r in schedule) == ["Feed", "Walk"]
    assert all(r["Status"] == "Pending" for r in schedule)
    assert any("Walk" in w.value and "Feed" in w.value for w in app.warning)
    # History is retained in the all-tasks table.
    assert "Done" in [r["Status"] for r in table_rows(app)]


def test_generate_schedule_with_no_pending_tasks_shows_error(app):
    click(app, "Generate schedule")
    assert any("Nothing to schedule" in e.value for e in app.error)

    add_pet(app, "Mochi")
    add_task(app, "Mochi", "Vet")
    done_button(app, "Vet").click().run()
    click(app, "Generate schedule")
    assert any("Nothing to schedule" in e.value for e in app.error)


# --- Duplicate pets, weekly recurrence and repeated completion through the UI ---


def test_duplicate_pet_name_shows_error_and_keeps_one_pet(app):
    add_pet(app, "Mochi")
    add_pet(app, "Mochi", "cat")

    assert any("already exists" in e.value for e in app.error)
    assert [p.name for p in app.session_state.owner.pets] == ["Mochi"]
    assert app.session_state.owner.pets[0].species == "dog"


def test_weekly_task_recurs_seven_days_later_through_the_ui(app):
    add_pet(app, "Mochi")
    add_task(app, "Mochi", "Bath", frequency="weekly")  # 2026-10-17 09:00

    done_button(app, "Bath").click().run()
    assert [(r["Time"], r["Status"]) for r in table_rows(app)] == [
        ("2026-10-17 09:00", "Done"),
        ("2026-10-24 09:00", "Pending"),  # exactly seven days later
    ]

    done_button(app, "Bath").click().run()  # complete that occurrence too
    assert [(r["Time"], r["Status"]) for r in table_rows(app)] == [
        ("2026-10-17 09:00", "Done"),
        ("2026-10-24 09:00", "Done"),
        ("2026-10-31 09:00", "Pending"),
    ]


def test_repeated_completion_attempts_do_not_duplicate_in_the_ui(app):
    from pawpal_system import Scheduler

    add_pet(app, "Mochi")
    add_task(app, "Mochi", "Walk", frequency="daily")
    button = done_button(app, "Walk")
    original = next(t for t in app.session_state.owner.get_all_tasks() if t.description == "Walk")

    button.click().run()
    # Stale second click on the same button, then direct repeated attempts on the same task.
    button.click().run()
    assert not any("Completed" in s.value for s in app.success)  # no new completion claimed
    assert [i.value for i in app.info] == ["'Walk' for Mochi was already completed."]
    assert len(app.session_state.owner.get_all_tasks()) == 2
    scheduler = Scheduler(app.session_state.owner)
    scheduler.complete_task(original)
    scheduler.complete_task(original)
    app.run()

    assert not app.exception
    assert [(r["Time"], r["Status"]) for r in table_rows(app)] == [
        ("2026-10-17 09:00", "Done"),
        ("2026-10-18 09:00", "Pending"),
    ]
