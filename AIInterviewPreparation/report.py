"""
report.py
Performance Report ("Results") module:
 - Shows Resume / Interview / Quiz / Communication scores as progress bars
 - Shows an overall percentage + grade
 - Shows AI suggestion cards
 - Lists locally saved report history (JSON files in /reports) and lets the
   user open any of them for a quick view.
"""

import json

import customtkinter as ctk

from utils import COLORS, FONT_FAMILY, grade_from_percentage, list_reports, load_json_report

SUGGESTION_POOL = {
    "resume": ["Add more measurable achievements to your resume", "Keep your resume to 1-2 pages"],
    "interview": ["Practice answering out loud to sound more natural", "Use the STAR method for behavioral questions"],
    "quiz": ["Revise core DBMS and SQL concepts", "Practice more Data Structures problems"],
    "communication": ["Speak more confidently and reduce filler words", "Maintain a clear structure: intro, body, conclusion"],
}


class ResultsFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=COLORS["background"])
        self.app = app
        self._build_ui()

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkLabel(
            scroll, text="📈 Performance Report", font=(FONT_FAMILY, 26, "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=10, pady=(15, 5))

        sd = self.app.session_data
        resume_score = sd.get("resume_score") or 0
        interview_score = sd.get("interview_score") or 0
        quiz_score = sd.get("quiz_score") or 0
        comm_score = sd.get("communication_score") or 0

        scores = [resume_score, interview_score, quiz_score, comm_score]
        overall = sum(scores) / len(scores) if scores else 0
        grade = grade_from_percentage(overall)

        # Overall summary card
        overall_card = ctk.CTkFrame(scroll, fg_color=COLORS["card"], corner_radius=14)
        overall_card.pack(fill="x", padx=10, pady=15)
        ctk.CTkLabel(overall_card, text=f"Overall Percentage: {overall:.1f}%",
                     font=(FONT_FAMILY, 20, "bold"), text_color=COLORS["accent"]).pack(
            anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(overall_card, text=f"Grade: {grade}",
                     font=(FONT_FAMILY, 16, "bold"), text_color=COLORS["text"]).pack(
            anchor="w", padx=20, pady=(0, 15))
        pb = ctk.CTkProgressBar(overall_card, progress_color=COLORS["accent"], height=16)
        pb.pack(fill="x", padx=20, pady=(0, 20))
        pb.set(overall / 100)

        # Individual score cards
        metrics_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        metrics_frame.pack(fill="x", padx=10, pady=5)

        self._add_metric_card(metrics_frame, "📄 Resume Score", resume_score, 0)
        self._add_metric_card(metrics_frame, "🎤 Interview Score", interview_score, 1)
        self._add_metric_card(metrics_frame, "🧠 Quiz Score", quiz_score, 2)
        self._add_metric_card(metrics_frame, "💬 Communication Score", comm_score, 3)

        for i in range(4):
            metrics_frame.grid_columnconfigure(i, weight=1)

        # Suggestions
        ctk.CTkLabel(
            scroll, text="💡 AI Suggestions", font=(FONT_FAMILY, 18, "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=10, pady=(25, 10))

        sug_row = ctk.CTkFrame(scroll, fg_color="transparent")
        sug_row.pack(fill="x", padx=10)
        all_suggestions = []
        if resume_score < 80:
            all_suggestions += SUGGESTION_POOL["resume"]
        if interview_score < 80:
            all_suggestions += SUGGESTION_POOL["interview"]
        if quiz_score < 80:
            all_suggestions += SUGGESTION_POOL["quiz"]
        if comm_score < 80:
            all_suggestions += SUGGESTION_POOL["communication"]
        if not all_suggestions:
            all_suggestions = ["Excellent performance across all areas — keep it up!"]

        for i, s in enumerate(all_suggestions[:6]):
            card = ctk.CTkFrame(sug_row, fg_color=COLORS["card"], corner_radius=12)
            card.grid(row=i // 2, column=i % 2, padx=8, pady=8, sticky="nsew")
            sug_row.grid_columnconfigure(i % 2, weight=1)
            ctk.CTkLabel(card, text=f"✓ {s}", font=(FONT_FAMILY, 12),
                         text_color=COLORS["text"], wraplength=320, justify="left").pack(
                padx=15, pady=15, anchor="w")

        # History
        ctk.CTkLabel(
            scroll, text="🗂  Interview History (Saved Reports)",
            font=(FONT_FAMILY, 18, "bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=10, pady=(25, 10))

        self.history_container = ctk.CTkFrame(scroll, fg_color=COLORS["card"], corner_radius=14)
        self.history_container.pack(fill="x", padx=10, pady=5)
        self._populate_history()

    def _add_metric_card(self, parent, title, value, col):
        card = ctk.CTkFrame(parent, fg_color=COLORS["card"], corner_radius=14)
        card.grid(row=0, column=col, padx=8, pady=8, sticky="nsew")
        ctk.CTkLabel(card, text=title, font=(FONT_FAMILY, 13, "bold"),
                     text_color=COLORS["secondary"]).pack(padx=15, pady=(15, 5), anchor="w")
        ctk.CTkLabel(card, text=f"{value:.1f}%", font=(FONT_FAMILY, 22, "bold"),
                     text_color=COLORS["text"]).pack(padx=15, anchor="w")
        pb = ctk.CTkProgressBar(card, progress_color=COLORS["primary"], height=10, width=180)
        pb.pack(padx=15, pady=(8, 15), anchor="w")
        pb.set(max(0, min(100, value)) / 100)

    def _populate_history(self):
        for widget in self.history_container.winfo_children():
            widget.destroy()

        reports = list_reports()
        if not reports:
            ctk.CTkLabel(self.history_container, text="No saved reports yet. Complete an activity to generate one.",
                         font=(FONT_FAMILY, 12), text_color=COLORS["text_muted"]).pack(padx=20, pady=20)
            return

        for filename, path in reports[:15]:
            row = ctk.CTkFrame(self.history_container, fg_color="transparent")
            row.pack(fill="x", padx=15, pady=5)
            ctk.CTkLabel(row, text=filename, font=(FONT_FAMILY, 12), text_color=COLORS["text"],
                         anchor="w").pack(side="left", fill="x", expand=True)
            ctk.CTkButton(row, text="View", width=70, height=28, corner_radius=8,
                          fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                          command=lambda p=path: self._view_report(p)).pack(side="right")

    def _view_report(self, path):
        try:
            data = load_json_report(path)
        except Exception as e:
            data = {"error": str(e)}

        win = ctk.CTkToplevel(self)
        win.title("Report Viewer")
        win.geometry("600x500")
        win.configure(fg_color=COLORS["background"])

        box = ctk.CTkTextbox(win, fg_color=COLORS["card"])
        box.pack(fill="both", expand=True, padx=15, pady=15)
        box.insert("1.0", json.dumps(data, indent=2))
        box.configure(state="disabled")

    def refresh(self):
        """Called by main app when navigating back to this frame so the
        displayed scores and history reflect the latest session data."""
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
