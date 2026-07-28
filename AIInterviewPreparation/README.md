# AI Interview Preparation

A modern, offline-first Windows desktop application built with **Python + CustomTkinter**
to help candidates prepare for job interviews: resume analysis, mock interviews
(typed + voice), technical quizzes, HR question practice, performance reports,
and a downloadable completion certificate.

No database is used — everything is stored locally as plain files (JSON reports,
copies of uploaded resumes, and generated PDF certificates) inside the project folder.

---

## Features

| Module | Description |
|---|---|
| 🏠 Dashboard | Welcome screen, quick stats, and shortcuts into every feature |
| 📄 Resume Analysis | Upload a PDF/DOCX resume → extracts name, email, phone, skills, education, projects, experience → Resume Score /100 + improvement suggestions |
| 🎤 Mock Interview | Randomized interview questions each session, typed **or voice** answers (offline speech-to-text where available), lightweight instant feedback |
| 🗣 HR Questions | 50+ common HR questions, one at a time, with model answers revealed after you submit |
| 🧠 Technical Quiz | 20-question MCQ quizzes across Python, Java, DBMS, SQL, OS, Computer Networks, Data Structures, and Web Development — shows correct/wrong answers, score, and percentage |
| 📈 Results | Resume / Interview / Quiz / Communication scores as progress bars, overall percentage + grade (A+ / A / B / C), AI suggestion cards, and history of saved reports |
| 🏆 Certificate | Generates a professional PDF certificate with your name, score, date, and a unique certificate number — preview, download, or print |
| ⚙ Settings | Dark/Light theme, enable/disable voice, clear saved reports, About |

---

## Project Structure

```
AIInterviewPreparation/
├── main.py                # App entry point — window, layout, navigation
├── ui.py                  # Sidebar navigation + Settings frame
├── dashboard.py            # Home dashboard frame
├── resume.py               # Resume parsing, scoring, and its UI frame
├── interview.py            # Mock interview (typed + voice) frame
├── quiz.py                  # Technical quiz frame
├── hr_questions.py          # HR questions frame
├── speech.py                # Offline-first speech-to-text wrapper
├── certificate.py           # PDF certificate generator + UI frame
├── report.py                 # Performance report / Results frame
├── utils.py                  # Shared colors, paths, settings, helpers
├── data/
│   ├── quiz_bank.py          # MCQ question bank (8 topics)
│   ├── hr_bank.py             # 50 HR questions + model answers
│   └── interview_bank.py      # Mock interview questions
├── assets/
│   ├── logo.png
│   ├── icon.ico
│   └── certificates/
├── reports/                    # Saved JSON performance reports (auto-created)
├── resumes/                     # Copies of uploaded resumes (auto-created)
├── certificates/                 # Generated certificate PDFs (auto-created)
├── data/settings.json             # User settings (auto-created on first run)
├── requirements.txt
└── README.md
```

---

## Setup (Development)

1. Make sure you have **Python 3.10+** installed on Windows.
2. Open a terminal in the project folder and create a virtual environment (recommended):
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   > If `PyAudio` or `pocketsphinx` fail to install, that's OK — the app still runs.
   > Only the voice-answer button will be disabled; typed answers work as normal.
   > On Windows, if `pip install PyAudio` fails, try:
   > `pip install pipwin` then `pipwin install pyaudio`.
4. Run the app:
   ```
   python main.py
   ```

---

## Building the Standalone .exe

Once dependencies are installed, build a single-file Windows executable with PyInstaller:

```
pyinstaller --onefile --windowed --icon=assets/icon.ico main.py
```

- The finished `AIInterviewPreparation.exe` (actually named `main.exe` unless you
  add `--name AIInterviewPreparation`) will be inside the generated `dist/` folder.
- **Important:** copy the `assets/` and `data/` folders next to the `.exe` inside
  `dist/` so the app can find the logo, icon, and question banks at runtime
  (PyInstaller's `--onefile` mode only bundles Python code by default, not
  loose data folders referenced by relative path).
- Recommended full command with a custom name:
  ```
  pyinstaller --onefile --windowed --icon=assets/icon.ico --name AIInterviewPreparation main.py
  ```

On first run, the app automatically creates the `reports/`, `resumes/`,
`certificates/`, and `data/settings.json` files/folders next to the executable
if they don't already exist — no manual setup or database required.

---

## Notes on Voice Interview

The Voice Interview feature uses the `speech_recognition` library. It first
tries **CMU Sphinx** (fully offline, via `pocketsphinx`) so the whole app can
run without an internet connection. If Sphinx isn't installed, it falls back
to Google's free Web Speech API (requires internet). If neither is available,
the app stays fully functional — you can simply type your answers instead.

---

## Tech Stack

- **UI:** CustomTkinter (dark/light themed, rounded buttons, hover effects)
- **Resume parsing:** pdfplumber / PyPDF2 (PDF), python-docx (DOCX)
- **Certificates:** ReportLab (PDF generation)
- **Speech-to-text:** SpeechRecognition + PocketSphinx (offline) / Google (online fallback)
- **Packaging:** PyInstaller (`--onefile --windowed`)
