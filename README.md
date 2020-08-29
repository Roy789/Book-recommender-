# COMP9900

## Rock n Roll

## CAPSTONE PROJECT - ReadRecommend

### final Software quality submission - https://github.com/unsw-cse-capstone-project/capstone-project-rock-n-roll/blob/master/FinalSubmission_RocknRoll.zip

### Introduction

> Many people like reading, and they're often on the look-out for the next interesting book to read.
> ReadRecommend is a platform that looks to provide a platform for readers to express their opinion on books
> they've read and liked, as well as a way to find new interesting books to read. One of the key abilities of
> ReadRecommend is providing readers with the ability to choose from multiple modes of recommendations.

### Installation

> \$pip install -r requirements.txt

#### To run the application from localhost, Download the whole project or use clone command:

> \$ git clone https://github.com/unsw-cse-capstone-project/capstone-project-rock-n-roll.git
>
> \$ cd capstone-project-rock-n-roll-master/
>
> \$ python main.py
>
> - Running on http://127.0.0.1:8001/ (Press CTRL+C to quit)

### Interface: HTML, CSS3, JavaScript, Bootstrap

> Bootstrap is open-source CSS framework directed at responsive web development. in combination with HTML and CSS we have generated
> user-friendly UI for login,register,main books page, user collections, and user account pages. To have specific event-trigger elements, JavaScript is utilised.

### Recommender: flask, dash, python

### Databse: SQLite

> This folder consists of all the important files needed for making the database locally. Please ensure that you have sqlite3 package intalled in your machine
> Steps:
>
> 1.  Replicating the Readrecommend database in your machine you need to run the following code:
>
> - python3 databasedesign.py This code will run the python script and make the important tables locally (in your working directory).
>
> 2.  Adding the functionality for adding a user after they sign up, the functions are created in the signup.py file.
>     This file has the function add_complete_user which takes the >following params:
>
> - Username
> - Password
> - Interests
> - question1 (This is the security question)
> - answer1 (Answer to the first question)
> - question2
> - answer2 This function will add a new user in our database if the username is unique.
>
> 3.  Populate the book database with all the important books that willl be used in our database, This is loaded and running 'python3 popbooks.py' will fill the books in the database.

### About us

#### z5226251 and z5179407 - Backend developers.

#### z5219466 - Front end developer.

#### z5225807 - Scrum manager.
