## Backlog, Sprint #1

The following tasks is what our team is scheduling to do in Sprint #1. In this sprint, we only focus on basic functions and building a working skeleton framework. We will not spend much effort on web page styles, say, designing fancy appearances for our web pages using bootstrap templates.

| Feature Category                | Feature Content                          | Estimated Hours | Feature Owner |
| :------------------------------ | :--------------------------------------- | :-------------: | :------------ |
| Authentication System           | Users are able to create new accounts and select their grades using  Django authentication system. |        1        | Tianyu Hong   |
| Authentication System           | Users can modify all of the properties and upload profile pages  associated to their account. |        2        | Tianyu Hong   |
| Authentication System           | Users creates account with email verification. User can retrieve  passwords by their email address. |        1        | Tianyu Hong   |
| Authentication System           | Create static templates of authentication system. |        3        | Tianyu Hong   |
| Friendship: Basics              | Users can connects to friends by searching names of friends. Friend searching process retrieves a list that matches the searching criteria. |        3        | Tianyu Hong   |
| Learning: Basics                | Add sample questions for two different grades with different categories  to database. A page can retrieve one random question from corresponding  grades in the dataset. |        3        | Tianyu Hong   |
| Learning: Basics                | The page can detect if the answer is right or wrong and tell user the  correct result. |        1        | Tianyu Hong   |
| Learning: Basics                | User can answer a set of questions randomly retrieved from dataset with  no duplicates. User can be informed that there is no further question to  learn. |        3        | Tianyu Hong   |
| Learning: Basics                | Users can keep track of their correctly answered questions. If they are  start again, they will not meet the previously correctly answered question  unless they choose to reset the study progress. |        5        | Tianyu Hong   |
| Learning: Basics                | Create static templates for learning page |        4        | Tianyu Hong   |
| Contest: Fundamental Techniques | Build an 'active user tracking' function using Django channels. Everyone  logged in is able to know which user is active and logged-in. |        5        | Fan Wu        |
| Contest: Messaging              | Extend the existing system using Django channels. Everyone who is inside the chatroom (same page) can post chat messages. Everyone in the chatroom can  receive chat messages real-time. |        5        | Fan Wu        |
| Contest: Invitation             | User can send contest challenging request to another user and only these two users can join the contest (same page) and messaging with each other. |        5        | Fan Wu        |
| Contest: Basics                 | Two users in the same page are able to start contest and answer a single question. The user who made correct answer first will get the credit. |        5        | Fan Wu        |
| Contest: Basics                 | Extend the above functionality to several random questions and calculate the final score of each person. Judge the final winner of the contest and save results in database |        5        | Fan Wu        |
| Contest: Basics                 | Create static templates for contest page |        5        | Fan Wu        |
| Game: Memorizing Game           | Create data models for pictures and words. Create canvas that contains pictures and words. |        5        | Tianyu Hong   |
| Game: Memorizing Game           | The system can fetch 10 random pictures and words and add them to canvas. |        4        | Fan Wu        |
| Game: Memorizing Game           | Player can see the revealed relationship between pictures and words. The  timer is set to 10 seconds. |        2        | Fan Wu        |
| Game: Memorizing Game           | Create a shuffle animation.              |        5        | Tianyu Hong   |
| Game: Memorizing Game           | Shuffle pictures and words and keep their original behaviors. |        4        | Fan Wu        |
| Game: Memorizing Game           | If players  correctly chose a pair, then the pair will stay turned. If players do not  choose a correct pair, the pair will be back to reverse status. |        5        | Fan Wu        |
| Game: Memorizing Game           | Set timer to the game and record final score to the games. |        4        | Fan Wu        |