# TALKY
#### Video Demo:  https://www.youtube.com/watch?v=Q2Ns1N2bEjw
#### Description:
<br>
CS50x FINAL PROJECT - TALKY

Talky is a quiz app that helps users practice their language learning vocabulary. Upon registering/logging in, users have the option of choosing between 3 quizzes to help improve their words, phrases or verbs vocabulary.

The quiz provides 5 multiple choice questions and evaluates the user's score at the end of the quiz.

Administators can also login to the backend where they can add, remove or update any data that is presented to the users in the quizzes.


---

## Technologies
<br>
- Flask was the web app framework used which handled URL routing and provided the Jinja template engine for creating markup.
- Python is the language used for Flask
- SQLite is the library used for the database
- HTML/CSS/Javascript were used on the front end in the browser, in particular for the quizzes.

---
## Main Files and Folders
<br>
- app.py - This file contains all the routes to each web page, the specified template to be shown along with any data or functionality that needs to be used on that route.
- helpers.py - This file contains the login helper function which is used as a decorator on any required routes. Basically users have to be logged in to be able to access majority of the pages on the site, otherwise they're redirected to the login page.
- talky.db - This is the database file the stores data comprising of all the tables, table fields, field data types etc. We can access the database and it's data using myPHPadmin through this file
- requirements.txt - a file with information about the required libraries, modules and packages that are being used in this web app

- templates folder - There are many template folders but the main ones to note are:
    - layout.html - This file provides the HTML markup for the pages on the **admin's front end**. The other pages on the admin's front end then extends this particular layout to save from DRY code
    - user-layout.html - Similar to layout.html, this provides HTML markup for the pages on the **user's front end**. Pages on the user's front end then extend this html file.
    - The remaining .html files - These files all contain HTML markup to display a particular page on the front end.
    - The words-quiz.html, phrases-quiz.html and verbs-quiz.html files extend not only the user-layout.html file but also contain a significant amount of Javascript code that relates to the quiz itself. This code updates the quiz progress bar, the questions and answers and the buttons pertaining to the quiz.
<br>
<br>
- static folder
    - This folder contains the css and javascript files that apply styling and functionality to every page on the site

---
## Design
<br>
The Admin pages have minimal UI design effort, mainly because its purpose to talk to the database and perform CRUD functions. Instead, more effort was put into the UI for the user front end including interactivity.

If I were to do this project again, I'd probably research more on how to include React JS and incorporate it into the project to use for the quizzes instead of Vanilla Javascript. The reason being is that with React, you can break up all the necessary components and organise everything in different files, folders etc. Using Vanilla Javascript in the way I did made each file very bulky and difficult to keep track of functions, hoisting etc.

Another thing I'd probably more carefully consider is whether or not to use Bootstrap in my project. The reason is on more than one occasion, I had many class conflictions and abnormal behaviour in my code which I found very difficult to debug. In saying so, it did save me a lot of time writing components from scratch.

---
## Conclusion
<br>
This project has helped me build the foundations for Python and SQLite and gave me extensive experience with Flask and the Jinja template engine.
I feel confident to continue expanding my knowledge and building on these foundations in these languages/frameworks.
<br>
<br>
Robert Garofalo
(https://www.robertgarofalo.com)
<br>
<br>
