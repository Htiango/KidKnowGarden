Project Specification Feedback
==================

Commit graded: cd838008e603db84111bf8b5fa2d1c39b63d79fb

### The product backlog (9/10)

You should have  a clear assignment of responsibility for each feature, to the student or students on the team who will complete that feature.  Each student should have sole responsibility for some features on the overall project.

You should have a cost estimate for each feature, in hours. If the cost estimate is more than 5 or 8 hours, you should consider breaking the feature into smaller work units to improve your ability to track progress on it.

A spreadsheet-like format is easier to read for backlogs, rather than prose or bulleted lists. You could also consider exploring existing online tools for generating and tracking work on a project.

If you are going to make a sudoku function, you probably should have more than a small set of hardcoded puzzles. Consider using online APIs to generate sudoku puzzles. Checking the validity of an answer should be simple.

With the battle feature, it sounds like you may want to make use of WebSockets for real time communication.

### Data models (9/10)

I'm not sure what you require the Category model for. Unless you plan to have more information for each category, it would be simpler and cleaner to have category as a field in each of the other models. Searching for a specific category would just be searching the model for category="some_category".

It's not clear how the Question choices and answer fields are organized. I assume since the answer field is an integer, these are multiple choice questions. Will all the questions have the same number of choices? If so, you could just have fields for options a, b, c, etc.

Are friends going to be a one way relationship like Follow or will it be symmetrical? This doesn't influence your models, but just something to think about.

You only have a model for you Question game. What about the other two games?

You should probably have more information under UserStats. For example, which game was played at what level.

### Wireframes or mock-ups (10/10)

Just a preference, but it would probably be useful to have each of the links on the homepage as a navbar link.

### Additional Information

---
#### Total score (28/30)
---
Graded by: Vivian Wang (vivianwa@andrew.cmu.edu)
