# GradeGuard 🎓

## Overview

GradeGuard is a Flask web app for graduate students who want real-time, quantitative insight into their course grades. Unlike Canvas, which assumes each item is out of 100, GradeGuard lets you enter **raw scores** (e.g. 34/34, 46/48) exactly as they appear on your assignments. It computes weighted grades across custom categories with full support for **drop-lowest**, **best-of-N** policies (e.g. best 8 of 10), and saves each course to memory so you can revisit and update it anytime.

Built for CS515 Fundamentals of Computing at Stevens Institute of Technology.

## Features

**Course Grade Calculator**
- Enter each category (Homework, Midterm, Final, etc.) with its grade weight
- Input raw scores as `earned / max` — e.g. 34/34, 46/48, 17/20
- Set total number of assignments and populate them all at once
- Toggle "Drop Lowest" per category
- "Best of N" support — e.g. keep best 8 out of 10 homeworks
- Live weight validator bar shows when weights sum to 100%

**What-If Score Solver**
- Enter your current grades and see what score you need on a future assignment to hit your target
- Color-coded result: green (doable), amber (grind), red (impossible)

**Exam Panic Ranker**
- Add upcoming exams with your current score, days until exam, and hours studied
- Algorithmic panic score ranks exams by urgency so you know where to focus first

**Course Memory**
- Save any course to persistent memory with one click
- Reload it from the sidebar any time — all your categories and scores come back
- Edit and re-save without affecting other saved courses
- Delete courses you no longer need

## Usage Instructions

### Prerequisites

- Python 3.10+
- pip

### Setup & Run

```bash
git clone <your-repo-url>
cd gradeguard
pip install -r requirements.txt
python app.py
```

Open your browser to local host (eg:`http://127.0.0.1:5000`)

### Running Tests

```bash
python test_hw7.py -v
```

All 18 unit tests should pass.

### Deploying to Render (Free)

1. Push the repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service → connect repo
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Deploy — your app is live at a public URL

## Tech Stack

- Python 3 / Flask
- Vanilla JavaScript (Fetch API, no frameworks)
- HTML5 / CSS3 (CSS Grid, Custom Properties, transitions)
- Google Fonts: Fraunces, Outfit, Space Mono

## Project Structure

```
gradeguard/
├── app.py               # Flask routes + REST API
├── hw7.py               # Core grade logic (Course, GradeCalculator, panic funcs)
├── test_hw7.py          # 18 unit tests
├── requirements.txt
├── courses_store.json   # Auto-created when you save a course
├── templates/
│   └── index.html
└── static/
    ├── css/style.css
    └── js/app.js
```

## Developers

- **Rishi Annam** — Backend logic, Flask API, frontend design
- **Haris Iqbal Butt** — Backend logic, Flask API, frontend design
