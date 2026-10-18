# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design for PawPal+ focuses on creating a simple and organized pet care management system using Object-Oriented Programming (OOP). The goal is to help pet owners manage their pets' daily activities, such as feeding, walking, medication, and appointments.

I included four main classes:

1. Owner: Stores the owner's information and manages multiple pets. It allows the owner to add pets and access all their scheduled tasks.
2. Pet: Stores information about each pet, such as its name and species, along with its list of tasks. It allows tasks to be added and viewed.
3. Task: Represents an individual activity, including its description, scheduled time, frequency, and completion status. It includes a method to mark a task as completed.
4. Scheduler: Organizes tasks across all pets. It handles sorting tasks by time, filtering tasks, identifying scheduling conflicts, and managing recurring activities.

The relationships are straightforward: **one Owner can have multiple Pets, each Pet can have multiple Tasks, and the Scheduler manages tasks across all Pets.**

I chose this design because it separates responsibilities between classes, making the code easier to understand, test, maintain, and extend as new features are added.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

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
