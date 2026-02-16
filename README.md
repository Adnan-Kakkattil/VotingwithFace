# College Voting System with Face Recognition

A secure, biometric-based web application for college student elections using Python Flask, OpenCV, and face recognition.

## Features

- **Admin Module** – Manage elections, candidates, and student access
- **Student Module** – Vote securely using face recognition
- **College Module** – Overview of elections and results
- **Candidate Module** – Nomination status and election statistics

## Tech Stack

- Python 3.10+
- Flask, SQLAlchemy, Flask-Login
- OpenCV, face_recognition, dlib
- Bootstrap 5

## Setup

### 1. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate    # Windows
# or: source venv/bin/activate  # Linux/Mac
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** Installing `dlib` may require CMake and a C++ compiler. On Windows, pre-built wheels are available for many Python versions.

### 3. Create admin user

```bash
python -m scripts.seed_admin
```

### 4. Run the application

```bash
python run.py
```

Open http://localhost:5000 and log in with:
- **Email:** admin@college.edu
- **Password:** admin123

## Project Structure

```
VotingwithFace/
├── app/
│   ├── __init__.py      # App factory
│   ├── models/          # User, Election, Candidate, Vote
│   ├── routes/          # Auth, Admin, Student, College, Candidate
│   ├── services/        # Face recognition service
│   └── templates/       # Jinja2 templates
├── config.py
├── run.py
├── requirements.txt
└── scripts/
    └── seed_admin.py
```

## License

Educational project.
