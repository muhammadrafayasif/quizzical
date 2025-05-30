
# Quizzical - CS50X FINAL PROJECT

## Program Execution
```
git clone https://github.com/muhammadrafayasif/quizzical.git
cd quizzical
python -m flask run
```
Provided the user has:
- git
- python
- flask
	- ``python -m pip install flask``

## Introduction
Quizzical is a flask based python web application that allows users to anonymously host and take multiple choice questions.
The web application has three simple functionalities:
- "Make a Quiz" page
- "Random" page
- "Take a Quiz" page

## Home Page
![Home page](https://i.ibb.co/vvJLkmCC/home.png)
The home page contains a simple interface with all the facilities of the website listed. When a quiz is inserted into the database, the home page will have a list of the most recent quizzes that the user can interact with,

## Make a Quiz
![Make a quiz](https://i.ibb.co/4gT3tktL/make-a-quiz.png)
The Make a Quiz page offers a fairly simple question and answer designer. After the user has created a quiz, the contents will be stored onto a sqlite3 database and will be given an ID number which can be used to access the quiz as a quiz taker.
"Make a Quiz" doesn't require any user registration and is done completely anonymously.

## Random Page
The random page will query the quizzes available in the database and pick a random one, this is fairly simple.

## Dependencies
- python
	- flask
	- sqlite3
	- json
	- datetime
	- random
