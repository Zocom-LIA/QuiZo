# QuiZo
# Team-a Bug Squashers
![image](https://github.com/user-attachments/assets/46aa2610-d90f-41e5-af8e-cdd6b91b27fb)


## Introduction
This Quiz App is an interactive platform designed for educators to create and manage quizzes and for students to take quizzes and receive instant feedback. It simplifies creating, updating, and deleting quizzes and offers a seamless experience for students to test their knowledge in various computer science subjects.

## Features
### Teachers Module
- Create quizzes with titles, descriptions, and multiple-choice questions.
- Create Edit or delete existing quizzes and questions
- Review results and statistics from student performances. (optional)

### Students Modeul
- Browse and select from a list of available quizzes.
- Take quizzes and submit answers.
- View scores immediately after submission.

## Technologies Used
- **Editor:** Visual Studio Code
- **Frontend:** HTML, CSS, JavaScript
- **Backend:** AWS Lambda (Python), API Gateway
- **Database:** DynamoDB
- **Storage and Deployment:** S3, AWS CLI SAM CLI
- **Version Control:** GitHub

## Setup Instructions

Setting up this project involves several steps including configuring your local development environment, setting up AWS services, and deploying the application using AWS SAM CLI.

### Prerequisites
- AWS account: AWS account set up with administrative access. (don't share any credential in Github)
- AWS CLI: Install and configure the AWS CLI with `aws configure`. (don't share keys in GitHub)
- Node.js and NPM: Required for using AWS SAM CLI and other possible build tools.
- AWS SAM CLI: Install the SAM CLI to handle local development and deployment.

### Clone the Repository
Start by cloning the repository to get the local copy of the source code.
```bash
git clone https://github.com/Zocom-LIA/AWS-BugSquashers.git
cd quiz-app
