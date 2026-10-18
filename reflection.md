# PawPal+ Project Reflection

## 1. System Design

### a. Initial Design

My initial UML design for PawPal+ focused on building a simple pet care management system using Object-Oriented Programming (OOP). The goal was to help pet owners organize daily activities such as feeding, walking, medication, and appointments for multiple pets.

I designed four main classes, each with a specific responsibility:

1. **Owner:** Stores the owner's name and manages multiple pets. It includes methods to add, remove, and find pets, as well as retrieve scheduled tasks across all pets.

2. **Pet:** Stores information about each pet, including its name, species, age, and list of tasks. It includes methods to add and remove tasks and retrieve pending activities.

3. **Task:** Represents an individual pet care activity. It stores the task description, scheduled date and time, frequency, associated pet name, and completion status. It includes methods to mark a task as completed and calculate the next occurrence of a recurring task.

4. **Scheduler:** Organizes and manages tasks across multiple pets. It handles sorting tasks chronologically, filtering tasks by pet or completion status, detecting scheduling conflicts, and completing tasks while managing their recurrence.

In my UML diagram, one Owner can have zero or more Pets, and each Pet can have zero or more Tasks. The Scheduler connects to the Owner to retrieve and manage tasks across all pets.

I chose this structure because it separates the responsibilities of storing information and managing scheduling logic. This makes the application easier to understand, test, maintain, and extend without making any single class too complicated.

### b. Design Changes

After creating my initial UML diagram and Python class skeleton, I asked Claude to review the design for missing relationships, unnecessary dependencies, and potential logic issues.

Claude confirmed that the four classes had clear responsibilities and that their relationships were appropriate. However, it identified several improvements that could make the application more reliable.

One suggestion I accepted was to have `Scheduler.get_all_tasks()` call `Owner.get_all_tasks()` instead of implementing the same retrieval logic twice. This avoids code duplication and keeps task retrieval in one place.

I also accepted the suggestion to make `Pet.add_task()` automatically update `task.pet_name` to match the pet's name. This helps maintain consistency between a task and the pet that owns it.

For conflict detection, I chose to check whether two pending tasks have exactly the same scheduled date and time instead of implementing more complicated overlapping-time calculations. This approach was easier to understand, implement, and test while still addressing the basic scheduling conflicts required by the project.

Another useful suggestion was to use `dataclasses.replace()` to generate recurring tasks. This allows the application to create a new pending task for the next day or week without changing the original task's details or completion history.

I also added frequency validation through `Task.__post_init__()`, which normalizes frequency values and rejects invalid inputs. For example, `" Daily "` becomes `"daily"`, while an invalid value such as `"dailly"` raises an error.

One change I made to the UML diagram was updating the Owner-to-Pet and Pet-to-Task relationships to use `0..*`, indicating that an owner can have zero or more pets and each pet can have zero or more tasks.

During implementation, I also refined the method return types. For example, `Owner.get_pet()` returns `None` when a pet is not found, `Task.next_occurrence()` returns `None` for one-time tasks, and `Scheduler.find_conflicts()` returns pairs of conflicting tasks.

I decided not to add task durations, advanced scheduling optimization, or priority-based scheduling during the initial implementation because they would introduce additional complexity.

After completing the changes, I used Claude to compare the Python implementation with my UML diagram. The final UML, saved in `diagrams/uml_final.mmd`, preserves the same four classes and relationships while reflecting the updated methods and return types.

Overall, this process taught me that AI-generated suggestions should be reviewed rather than automatically accepted. I learned to balance functionality, simplicity, and maintainability when making design decisions.

---

## 2. Scheduling Logic and Tradeoffs

### a. Constraints and Priorities

My scheduler primarily considers two things: **the scheduled date and time of each task and whether the task has been completed**.

The due date and time are used to sort tasks chronologically, identify scheduling conflicts, and calculate the next occurrence of recurring tasks.

The completion status helps separate pending tasks from completed activities. It is also used to prevent completed tasks from appearing in the pending schedule or being included in conflict detection.

The system supports three frequency options: `once`, `daily`, and `weekly`. For daily tasks, the next occurrence is scheduled one day later, while weekly tasks are scheduled seven days later. One-time tasks do not create another occurrence after completion.

I decided that time was the most important constraint because the main purpose of the application is to help pet owners organize activities throughout the day.

The current implementation does not use task duration or priority levels. Since these attributes are not part of my Task class, the scheduler cannot determine how long an activity will take or rank activities based on importance.

For this version, I focused on making chronological scheduling, filtering, and recurrence work reliably across multiple pets.

### b. Tradeoffs

One important tradeoff I made was keeping conflict detection simple.

My scheduler identifies a conflict only when two or more pending tasks have exactly the same date and time.

For example, if Mochi's breakfast and Luna's feeding are both scheduled for 8:00 AM, the system identifies a conflict and displays a warning.

However, if one task starts at 9:00 AM and another starts at 9:01 AM, the system does not identify a conflict, even if the first task might take 30 minutes.

I chose this approach because my tasks do not have a duration attribute, so the system cannot calculate overlapping time intervals accurately.

Claude discussed the possibility of more advanced conflict detection, but I decided to keep exact-time matching because it is easier to understand, implement, and test for a beginner-level application.

Another design decision was to use a dictionary to group pending tasks by their scheduled date and time and then use `itertools.combinations()` to generate unique conflicting pairs. This avoids comparing every task with every other task when there are no conflicts, although generating all pairs can still take more time when many tasks share the same time.

I think these tradeoffs are reasonable for a small pet care application. If the system were expanded to support many pets or more complex schedules, I would introduce task durations, priority levels, and overlap detection.

---

## 3. AI Collaboration

### a. How I Used AI

I used Claude as my AI coding assistant throughout the PawPal+ project, mainly for design review, implementation, debugging, testing, and documentation.

During the system design phase, I used Claude to review my UML diagram and Python class skeleton. I asked it to identify missing relationships, unnecessary dependencies, and potential logic problems before making changes.

During implementation, I divided the work into smaller tasks instead of asking Claude to build the entire application at once.

I started with the Task and Pet classes, moved to the Owner class, and then implemented the Scheduler. After completing the core logic, I used Claude to help create the command-line demonstration in `main.py` and connect the backend classes to the Streamlit interface in `app.py`.

I also used Claude to help write pytest tests, identify edge cases, and explain how different methods work.

For example, when implementing recurring tasks, I asked Claude to make sure completing a task would create the next occurrence without modifying the original task or creating duplicates.

I found that specific prompts worked better than broad instructions. The most helpful prompts clearly explained the method to implement, the expected behavior, the files Claude could modify, and the tests it needed to run.

I also frequently asked Claude to review the existing code before making changes and to explain the results of its terminal checks.

This approach made the development process more organized and helped me understand the code while building it.

### b. Judgment and Verification

I learned that using AI effectively involves evaluating its suggestions and verifying that the generated code behaves as expected.

One example was conflict detection. Although adding task durations and more advanced overlap detection could improve the application, I chose to use exact-time conflicts because that was appropriate for the project's scope.

I also accepted some recommendations that improved the overall design, such as delegating task retrieval to the Owner class, synchronizing pet names when tasks are added, and using `dataclasses.replace()` for recurring tasks.

After each implementation step, I reviewed the results and used terminal commands to verify functionality.

I ran `python main.py` to check the end-to-end scheduling workflow and `python -m pytest -v` to verify the automated tests.

One issue identified during verification involved the Streamlit "Mark done" button.

When an outdated button was clicked for an already completed task, the application displayed another success message even though the task was already marked complete. The underlying scheduling logic correctly prevented duplicate recurring tasks, but the message was misleading.

I worked with Claude to update the interface so it displays an informational message indicating that the task was already completed. I also updated the automated test to verify this behavior.

This experience showed me that passing tests alone is not enough. It is also important to verify whether the application's output and messages accurately represent what happened.

---

## 4. Testing and Verification

### a. What I Tested

With Claude's assistance, I developed and verified **43 automated test cases**, including 31 tests for the core Python logic and 12 tests for the Streamlit interface.

For the core classes, I tested task completion, task addition, synchronization of pet names, and retrieving tasks across multiple pets.

For the Scheduler, I tested chronological sorting, filtering by pet and completion status, conflict detection, and recurring task generation.

I also tested different recurrence behaviors. Daily tasks create a new pending occurrence one day later, weekly tasks create one seven days later, and one-time tasks do not recur.

Another important test verified that completing the same recurring task multiple times does not create duplicate occurrences.

For conflict detection, I tested tasks belonging to the same pet, tasks belonging to different pets, multiple tasks at the same time, and situations where completed tasks should be ignored.

I also tested invalid frequency inputs, frequency normalization, duplicate pet names, and attempts to complete tasks that belong to another owner.

For the Streamlit application, I tested input validation, session-state persistence, scheduling tasks, marking tasks complete, stable button keys, recurring task updates, and conflict warnings.

The Streamlit tests also verified that completed tasks remain in the history while being excluded from the pending schedule.

All **43 automated tests passed** in the latest verification run.

I also ran `python main.py`, which demonstrated the complete workflow using two pets, Mochi and Luna. The output showed tasks being sorted, a conflict between two activities scheduled at 8:00 AM, and a daily task creating its next occurrence after completion.

These tests were important because they helped verify the scheduling logic and interactions between the application's different components.

### b. Confidence

I would rate my confidence in the application at **4 out of 5**.

The core scheduling features work as intended in the tested scenarios, and all 43 automated tests pass. I also verified the command-line demonstration.

However, the Streamlit UI was primarily tested using Streamlit's automated testing framework rather than a complete manual browser walkthrough. I also did not measure the percentage of code covered by the tests.

If I had more time, I would add additional tests for removing pets and tasks, recurring tasks across month or year boundaries, and more complex scheduling conflicts.

I would also test how the application behaves when an owner manages many pets and tasks, and examine edge cases such as duplicate pet names with different capitalization.

Overall, I am confident that the core application works correctly for the functionality implemented, while recognizing that additional testing would be needed for a larger production system.

---

## 5. Reflection

### a. What Went Well

The part I am most satisfied with is how the original class design remained consistent throughout the project.

Starting with a UML diagram helped me understand the relationships between Owner, Pet, Task, and Scheduler before writing the implementation.

Building the classes one at a time also made the process easier to manage. I could test each component before moving to the next one, which helped prevent problems from becoming difficult to trace later.

I am especially satisfied with the recurring-task feature and conflict detection because they make the application more useful than a simple list of tasks.

The command-line demonstration helped me verify the backend independently, while the Streamlit interface made the application more interactive and user-friendly.

Another positive outcome was developing a comprehensive set of automated tests that verified the system's behavior across different scenarios.

### b. What I Would Improve

If I had another opportunity to improve PawPal+, I would focus on making the scheduler more flexible and practical.

First, I would add task duration and priority levels. This would allow the application to detect overlapping activities instead of only tasks scheduled at exactly the same time. It would also help the scheduler prioritize important activities, such as medication or veterinary appointments.

Second, I would introduce data persistence using JSON or a database. Currently, pets and tasks are stored in memory, so they are not permanently saved when the application session ends.

Third, I would improve how pet names are handled by making duplicate-name checking case-insensitive or introducing unique pet identifiers.

I would also consider adding features such as reminders, notifications, and a more detailed daily schedule.

Finally, I would expand the automated test coverage and perform additional browser-based testing to improve confidence in the application's reliability.

### c. Key Takeaway

My biggest takeaway from this project is the importance of designing a system before implementing it.

Creating the UML diagram first helped me identify the responsibilities of each class and understand how they should interact.

I also learned that AI tools are most useful when I provide clear instructions, review their suggestions, and independently verify the results.

Claude helped speed up development, but I still needed to make decisions about which features to implement, which suggestions to accept, and how to test the application.

Working through the project in smaller steps made the process easier to understand and helped me identify problems earlier.

Overall, PawPal+ helped me strengthen my understanding of Python OOP, modular system design, scheduling algorithms, automated testing, Streamlit integration, and responsible collaboration with AI tools.