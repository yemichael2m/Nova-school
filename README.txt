# Nova Learning Platform

A beginner-friendly multi-subject learning website built with Flask, SQLite, HTML, CSS and JavaScript.

## Run on Windows

1. Install Python 3 from https://www.python.org/downloads/ (check "Add Python to PATH").
2. Extract this ZIP folder.
3. Open Command Prompt in the `nova_gs_quiz` folder.
4. Run:

```bash
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py app.py
```

5. Open http://127.0.0.1:5000 in Chrome.

## Included
- Dashboard and subject selection
- Timed mixed quiz and chapter/subject filtering
- Instant question selection and final review
- SQLite storage for scores
- Local leaderboard
- Form to add your own questions
- Dark purple Nova dashboard inspired by the supplied reference image
- Nine subject areas: Mathematics, English, Amharic, General Science, Social Studies, Civics & Ethics, Health Education, ICT and Agriculture
- Nova Tutor chat: enter a supported topic, read an explanation and key points, then take a topic quiz
- English/Amharic dashboard language toggle
- Built-in starter lessons and quizzes for topics across all nine subject areas
- Add your own questions, view scores and leaderboard

## Important
The included questions are sample practice questions, not a verified copy of any specific Grade 8 textbook. Add questions from your own textbook using "Add questions".

This starter project runs locally. To put it on a public .com domain, deploy it to a Python-compatible hosting provider and connect a domain you own. Change the Flask secret key and disable debug mode before public deployment.

Note: this version includes a starter library, not every chapter in every textbook. For complete curriculum coverage, import the relevant textbook chapters/questions. The tutor is an offline topic library, not a connected generative AI service.


DEPLOYMENT PREPARATION
- Procfile and render.yaml are included for a Render deployment.
- Set a strong NOVA_SECRET environment variable in your hosting dashboard.
- Configure persistent storage for nova.db before using the site with real student records; the default SQLite file may be reset by some hosting providers on redeploy.
- Custom domain: register Nova-school.com with a domain registrar, then add it in the hosting dashboard and configure the DNS records shown by the host. Domain availability and ownership have not been verified.
- Public owner credit: Yemichael Fisseha.
