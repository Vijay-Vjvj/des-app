"""
resume.py
Resume Analysis module:
 - Parses PDF / DOCX resumes
 - Extracts Name, Email, Phone, Skills, Education, Projects, Experience
 - Computes a Resume Score out of 100
 - Provides improvement suggestions
 - Provides the CustomTkinter frame for this feature
"""

import os
import re
import shutil
import threading
from tkinter import filedialog, messagebox

import customtkinter as ctk

from utils import COLORS, FONT_FAMILY, RESUMES_DIR, save_json_report

# ----------------------------------------------------------------------------
# TEXT EXTRACTION
# ----------------------------------------------------------------------------

def extract_text_from_pdf(path: str) -> str:
    text = ""
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception:
        # Fallback to PyPDF2 if pdfplumber fails or isn't installed
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(path)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        except Exception as e:
            raise RuntimeError(f"Failed to read PDF: {e}")
    return text


def extract_text_from_docx(path: str) -> str:
    try:
        import docx
        document = docx.Document(path)
        return "\n".join(p.text for p in document.paragraphs)
    except Exception as e:
        raise RuntimeError(f"Failed to read DOCX: {e}")


def extract_resume_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return extract_text_from_pdf(path)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(path)
    else:
        raise ValueError("Unsupported file type. Please upload a PDF or DOCX file.")


# ----------------------------------------------------------------------------
# FIELD EXTRACTION
# ----------------------------------------------------------------------------

SKILL_KEYWORDS = [
    "python", "java", "c++", "c#", "javascript", "typescript", "html", "css",
    "sql", "mysql", "postgresql", "mongodb", "react", "angular", "vue",
    "node.js", "django", "flask", "spring", "aws", "azure", "gcp", "docker",
    "kubernetes", "git", "github", "linux", "excel", "power bi", "tableau",
    "machine learning", "deep learning", "data analysis", "pandas", "numpy",
    "tensorflow", "pytorch", "rest api", "api", "agile", "scrum", "c",
    "communication", "leadership", "problem solving", "teamwork",
]

SECTION_HEADERS = {
    "education": ["education", "academic background", "qualification"],
    "experience": ["experience", "work experience", "employment history", "professional experience"],
    "projects": ["projects", "academic projects", "personal projects"],
    "skills": ["skills", "technical skills", "key skills"],
}


def extract_email(text: str):
    match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)
    return match.group(0) if match else None


def extract_phone(text: str):
    match = re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3}[-.\s]?\d{3,4}", text)
    return match.group(0).strip() if match else None


def extract_name(text: str):
    # Heuristic: the first non-empty line that isn't an email/phone and is
    # short enough to plausibly be a person's name.
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if "@" in line or re.search(r"\d{3,}", line):
            continue
        if 2 <= len(line.split()) <= 4 and len(line) < 40:
            return line.title()
    return "Not Detected"


def extract_skills(text: str):
    text_lower = text.lower()
    found = []
    for skill in SKILL_KEYWORDS:
        # Skills containing only word characters get a strict word-boundary
        # match (so "c" doesn't match inside "certification"). Skills with
        # symbols (c++, c#) or spaces (machine learning) use a plain
        # substring search since \b doesn't work well around symbols.
        if re.fullmatch(r"[a-z0-9.]+", skill):
            pattern = r"(?<![a-z0-9])" + re.escape(skill) + r"(?![a-z0-9])"
            if re.search(pattern, text_lower):
                found.append(skill)
        else:
            if skill in text_lower:
                found.append(skill)
    return sorted(set(found), key=str.lower)


def _extract_section(text: str, keys):
    """Grab the block of text following a section header until the next
    recognized header or end of document."""
    lines = text.splitlines()
    lower_lines = [l.lower().strip() for l in lines]
    all_header_words = [w for words in SECTION_HEADERS.values() for w in words]

    start_idx = None
    for i, line in enumerate(lower_lines):
        for key in keys:
            if line.startswith(key) or line == key:
                start_idx = i + 1
                break
        if start_idx is not None:
            break

    if start_idx is None:
        return ""

    collected = []
    for line in lines[start_idx:start_idx + 25]:
        stripped_lower = line.lower().strip()
        if any(stripped_lower.startswith(h) for h in all_header_words) and stripped_lower not in keys:
            break
        collected.append(line)
    return "\n".join(collected).strip()


def extract_education(text: str):
    return _extract_section(text, SECTION_HEADERS["education"]) or "Not clearly detected"


def extract_experience(text: str):
    return _extract_section(text, SECTION_HEADERS["experience"]) or "Not clearly detected"


def extract_projects(text: str):
    return _extract_section(text, SECTION_HEADERS["projects"]) or "Not clearly detected"


# ----------------------------------------------------------------------------
# SCORING + SUGGESTIONS
# ----------------------------------------------------------------------------

def compute_resume_score(parsed: dict, raw_text: str):
    score = 0
    suggestions = []

    # Contact info (15 pts)
    if parsed["email"]:
        score += 8
    else:
        suggestions.append("Add a professional email address")
    if parsed["phone"]:
        score += 7
    else:
        suggestions.append("Add a contact phone number")

    # Skills (25 pts)
    skill_count = len(parsed["skills"])
    score += min(25, skill_count * 3)
    if skill_count < 5:
        suggestions.append("Add technical skills")

    # Education (15 pts)
    if parsed["education"] and parsed["education"] != "Not clearly detected":
        score += 15
    else:
        suggestions.append("Add a clear Education section")

    # Experience (20 pts)
    if parsed["experience"] and parsed["experience"] != "Not clearly detected":
        score += 20
    else:
        suggestions.append("Add a Work Experience section")

    # Projects (15 pts)
    if parsed["projects"] and parsed["projects"] != "Not clearly detected":
        score += 15
    else:
        suggestions.append("Improve project descriptions")

    text_lower = raw_text.lower()

    # GitHub / portfolio (5 pts)
    if "github" in text_lower or "portfolio" in text_lower:
        score += 5
    else:
        suggestions.append("Add a GitHub / portfolio link")

    # Certifications (5 pts)
    if "certificat" in text_lower:
        score += 5
    else:
        suggestions.append("Add relevant certifications")

    # Basic grammar/quality heuristic: very short resumes score lower
    word_count = len(raw_text.split())
    if word_count < 120:
        suggestions.append("Expand your resume with more detail (it looks quite short)")
    if not suggestions:
        suggestions.append("Great resume! Consider tailoring keywords for each job application.")
    else:
        suggestions.append("Proofread carefully to correct any grammar mistakes")

    return min(100, score), suggestions


def analyze_resume(path: str) -> dict:
    raw_text = extract_resume_text(path)
    if not raw_text.strip():
        raise ValueError("Could not extract any text from this file.")

    parsed = {
        "name": extract_name(raw_text),
        "email": extract_email(raw_text),
        "phone": extract_phone(raw_text),
        "skills": extract_skills(raw_text),
        "education": extract_education(raw_text),
        "projects": extract_projects(raw_text),
        "experience": extract_experience(raw_text),
    }
    score, suggestions = compute_resume_score(parsed, raw_text)
    parsed["score"] = score
    parsed["suggestions"] = suggestions
    return parsed


# ----------------------------------------------------------------------------
# UI FRAME
# ----------------------------------------------------------------------------

class ResumeFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=COLORS["background"])
        self.app = app
        self.last_result = None
        self._build_ui()

    def _build_ui(self):
        header = ctk.CTkLabel(
            self, text="📄 Resume Analysis",
            font=(FONT_FAMILY, 26, "bold"), text_color=COLORS["text"]
        )
        header.pack(anchor="w", padx=30, pady=(25, 5))

        subtitle = ctk.CTkLabel(
            self, text="Upload your resume (PDF or DOCX) to get an instant analysis and score.",
            font=(FONT_FAMILY, 14), text_color=COLORS["text_muted"]
        )
        subtitle.pack(anchor="w", padx=30, pady=(0, 15))

        upload_card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=14)
        upload_card.pack(fill="x", padx=30, pady=10)

        self.upload_btn = ctk.CTkButton(
            upload_card, text="⬆  Upload Resume (PDF / DOCX)",
            font=(FONT_FAMILY, 14, "bold"), fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"], corner_radius=10,
            height=45, command=self.upload_resume
        )
        self.upload_btn.pack(padx=20, pady=20)

        self.status_label = ctk.CTkLabel(
            upload_card, text="No file uploaded yet.",
            font=(FONT_FAMILY, 12), text_color=COLORS["text_muted"]
        )
        self.status_label.pack(padx=20, pady=(0, 15))

        # Scrollable results area
        self.results_frame = ctk.CTkScrollableFrame(
            self, fg_color="transparent"
        )
        self.results_frame.pack(fill="both", expand=True, padx=30, pady=10)

    def upload_resume(self):
        path = filedialog.askopenfilename(
            title="Select your resume",
            filetypes=[("Resume files", "*.pdf *.docx"), ("PDF files", "*.pdf"), ("Word files", "*.docx")]
        )
        if not path:
            return

        self.status_label.configure(text="Analyzing resume, please wait...")
        self.upload_btn.configure(state="disabled")

        thread = threading.Thread(target=self._analyze_worker, args=(path,), daemon=True)
        thread.start()

    def _analyze_worker(self, path):
        try:
            # Save a copy locally inside /resumes
            os.makedirs(RESUMES_DIR, exist_ok=True)
            dest = os.path.join(RESUMES_DIR, os.path.basename(path))
            try:
                shutil.copy(path, dest)
            except Exception:
                pass

            result = analyze_resume(path)
            self.after(0, self._show_results, result)
        except Exception as e:
            self.after(0, self._show_error, str(e))

    def _show_error(self, message):
        self.upload_btn.configure(state="normal")
        self.status_label.configure(text=f"Error: {message}")
        messagebox.showerror("Resume Analysis Failed", message)

    def _show_results(self, result: dict):
        self.upload_btn.configure(state="normal")
        self.status_label.configure(text="Analysis complete ✅")
        self.last_result = result
        self.app.session_data["resume_score"] = result["score"]

        for widget in self.results_frame.winfo_children():
            widget.destroy()

        # Score card
        score_card = ctk.CTkFrame(self.results_frame, fg_color=COLORS["card"], corner_radius=14)
        score_card.pack(fill="x", pady=10)
        ctk.CTkLabel(
            score_card, text=f"Resume Score: {result['score']} / 100",
            font=(FONT_FAMILY, 20, "bold"), text_color=COLORS["accent"]
        ).pack(anchor="w", padx=20, pady=(15, 5))
        progress = ctk.CTkProgressBar(score_card, progress_color=COLORS["accent"], height=14)
        progress.pack(fill="x", padx=20, pady=(0, 15))
        progress.set(result["score"] / 100)

        # Extracted info card
        info_card = ctk.CTkFrame(self.results_frame, fg_color=COLORS["card"], corner_radius=14)
        info_card.pack(fill="x", pady=10)
        ctk.CTkLabel(
            info_card, text="Extracted Information",
            font=(FONT_FAMILY, 16, "bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(15, 10))

        fields = [
            ("Name", result["name"]),
            ("Email", result["email"] or "Not detected"),
            ("Phone", result["phone"] or "Not detected"),
            ("Skills", ", ".join(result["skills"]) if result["skills"] else "Not detected"),
            ("Education", result["education"]),
            ("Projects", result["projects"]),
            ("Experience", result["experience"]),
        ]
        for label, value in fields:
            row = ctk.CTkFrame(info_card, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=4)
            ctk.CTkLabel(row, text=f"{label}:", font=(FONT_FAMILY, 13, "bold"),
                         text_color=COLORS["secondary"], width=100, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=str(value), font=(FONT_FAMILY, 13),
                         text_color=COLORS["text"], anchor="w", wraplength=550, justify="left").pack(
                side="left", fill="x", expand=True)
        ctk.CTkFrame(info_card, fg_color="transparent", height=10).pack()

        # Suggestions card
        sug_card = ctk.CTkFrame(self.results_frame, fg_color=COLORS["card"], corner_radius=14)
        sug_card.pack(fill="x", pady=10)
        ctk.CTkLabel(
            sug_card, text="Suggestions for Improvement",
            font=(FONT_FAMILY, 16, "bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(15, 10))
        for s in result["suggestions"]:
            ctk.CTkLabel(
                sug_card, text=f"✓ {s}", font=(FONT_FAMILY, 13),
                text_color=COLORS["accent"], anchor="w"
            ).pack(anchor="w", padx=20, pady=2)
        ctk.CTkFrame(sug_card, fg_color="transparent", height=10).pack()

        # Save report
        save_json_report("resume_report", result)
