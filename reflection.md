# PawPal+ Project Reflection

## 1. System Design

### a. Initial design

My initial UML design for PawPal+ focuses on building a simple pet care management system using Object-Oriented Programming (OOP). The goal is to help pet owners organize daily activities such as feeding, walking, medication, and appointments for multiple pets.

I included four main classes:

1. **Owner:** Stores the owner's information and manages multiple pets. It includes methods to add, remove, and find pets, as well as retrieve all their scheduled tasks.
2. **Pet:** Stores information about each pet, such as its name, species, age, and list of tasks. It allows tasks to be added, removed, and viewed.
3. **Task:** Represents an individual pet care activity. It stores the description, scheduled time, frequency, associated pet, and completion status. It includes methods to mark tasks as completed and calculate the next occurrence of recurring tasks.
4. **Scheduler:** Organizes tasks across multiple pets. It handles sorting tasks by time, filtering tasks by pet or completion status, detecting scheduling conflicts, and managing recurring activities.

In my UML diagram, one Owner can have multiple Pets, each Pet can have multiple Tasks, and the Scheduler accesses the Owner to manage tasks across all pets.

I chose this design because each class has a specific responsibility. This makes the code easier to understand, test, maintain, and extend as new features are added.

### b. Design changes

After creating my initial UML diagram and Python class skeleton, I asked Claude to review the design for missing relationships, unnecessary dependencies, and potential logic issues.

Claude confirmed that the four classes had clear responsibilities and that their relationships were appropriate. However, it also suggested a few improvements to make the application more reliable.

One suggestion I accepted was to have `Scheduler.get_all_tasks()` call `Owner.get_all_tasks()` instead of repeating the same logic. This avoids code duplication and keeps task retrieval in one place.

I also agreed with the suggestion to have `Pet.add_task()` automatically update `task.pet_name` to match the pet's name. This will help prevent inconsistencies between tasks and their associated pets.

For conflict detection, Claude recommended checking whether two tasks have the exact same scheduled time instead of implementing more complicated overlapping-time calculations. I chose this simpler approach because it is sufficient for the initial project and easier to understand and test.

Another useful suggestion was to use `dataclasses.replace()` when generating recurring tasks. This will allow the application to create a new task without modifying the original completed task.

I decided not to add advanced features such as task durations or complex scheduling optimization at this stage because they would introduce unnecessary complexity.

One change I made to my UML diagram was updating the relationships to use `0..*`, showing that an Owner can have zero or more Pets and each Pet can have zero or more Tasks.

After reviewing these suggestions, I asked Claude to compare my UML diagram with the Python class skeleton. Claude confirmed that the classes, attributes, methods, and relationships were consistent. Since the planned improvements only affect method implementations, I decided to keep the overall class structure unchanged.

This process helped me understand the importance of reviewing AI-generated suggestions rather than accepting everything automatically. I learned that a good system design should balance functionality, simplicity, and maintainability. I plan to implement the accepted improvements during the next development phases.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
