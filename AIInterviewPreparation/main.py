"""
main.py
Entry point for the AI Interview Preparation desktop application.

Run with:  python main.py
Build EXE: pyinstaller --onefile --windowed --icon=assets/icon.ico main.py
"""

import sys
from tkinter import messagebox

import customtkinter as ctk

from utils import COLORS, FONT_FAMILY, load_settings
from ui import Sidebar, SettingsFrame
from dashboard import DashboardFrame
from resume import ResumeFrame
from interview import InterviewFrame
from quiz import QuizFrame
from hr_questions import HRFrame
from report import ResultsFrame
from certificate import CertificateFrame

ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        settings = load_settings()
        ctk.set_appearance_mode("dark" if settings.get("theme", "dark") == "dark" else "light")

        self.title("AI Interview Preparation")
        self.geometry("1200x760")
        self.minsize(1000, 650)
        self.configure(fg_color=COLORS["background"])

        try:
            self.iconbitmap("assets/icon.ico")
        except Exception:
            pass

        # Shared state used across modules to build the final performance report
        self.session_data = {
            "resume_score": None,
            "interview_score": None,
            "quiz_score": None,
            "communication_score": None,
        }

        self.protocol("WM_DELETE_WINDOW", self.confirm_exit)

        self._build_layout()
        self.show_frame("Dashboard")

    def _build_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = Sidebar(self, self)
        self.sidebar.grid(row=0, column=0, sticky="nsw")

        self.content_area = ctk.CTkFrame(self, fg_color=COLORS["background"], corner_radius=0)
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_rowconfigure(0, weight=1)
        self.content_area.grid_columnconfigure(0, weight=1)

        # Frames are created once and re-shown (except Results, which refreshes
        # on every visit so it reflects the latest scores).
        self.frames = {
            "Dashboard": DashboardFrame(self.content_area, self),
            "Resume Analysis": ResumeFrame(self.content_area, self),
            "Mock Interview": InterviewFrame(self.content_area, self),
            "Technical Quiz": QuizFrame(self.content_area, self),
            "HR Questions": HRFrame(self.content_area, self),
            "Results": ResultsFrame(self.content_area, self),
            "Certificate": CertificateFrame(self.content_area, self),
            "Settings": SettingsFrame(self.content_area, self),
        }

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, name):
        if name not in self.frames:
            return
        frame = self.frames[name]

        # Keep dashboard + results fresh with the latest session scores
        if name == "Dashboard" and hasattr(frame, "refresh"):
            frame.refresh()
        if name == "Results" and hasattr(frame, "refresh"):
            frame.refresh()

        frame.tkraise()
        self.sidebar.set_active(name)

    def confirm_exit(self):
        if messagebox.askyesno("Exit Application", "Are you sure you want to exit?"):
            self.destroy()
            sys.exit(0)


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
