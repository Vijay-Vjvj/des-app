"""
hr_questions.py
HR Interview module: shows one HR question at a time, lets the user type an
answer, then reveals a model answer after submission.
"""

import random

import customtkinter as ctk

from utils import COLORS, FONT_FAMILY, save_json_report
from data.hr_bank import HR_QUESTIONS


class HRFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=COLORS["background"])
        self.app = app
        self.order = list(range(len(HR_QUESTIONS)))
        random.shuffle(self.order)
        self.current = 0
        self.session_log = []
        self._build_ui()
        self._load_question()

    def _build_ui(self):
        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(fill="x", padx=30, pady=(25, 5))
        ctk.CTkLabel(
            header_row, text="🗣  HR Interview Questions",
            font=(FONT_FAMILY, 26, "bold"), text_color=COLORS["text"]
        ).pack(side="left")

        self.counter_label = ctk.CTkLabel(
            header_row, text="", font=(FONT_FAMILY, 13), text_color=COLORS["text_muted"]
        )
        self.counter_label.pack(side="right")

        self.card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=14)
        self.card.pack(fill="both", expand=True, padx=30, pady=15)

        self.question_label = ctk.CTkLabel(
            self.card, text="", font=(FONT_FAMILY, 18, "bold"),
            text_color=COLORS["text"], wraplength=750, justify="left"
        )
        self.question_label.pack(anchor="w", padx=25, pady=(25, 15))

        self.answer_box = ctk.CTkTextbox(self.card, height=140, corner_radius=10,
                                          fg_color=COLORS["card_light"])
        self.answer_box.pack(fill="x", padx=25, pady=(0, 15))

        self.submit_btn = ctk.CTkButton(
            self.card, text="Submit Answer", height=40, corner_radius=10,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            command=self._submit_answer
        )
        self.submit_btn.pack(anchor="w", padx=25)

        self.model_label = ctk.CTkLabel(
            self.card, text="", font=(FONT_FAMILY, 13), text_color=COLORS["accent"],
            wraplength=750, justify="left"
        )
        self.model_label.pack(anchor="w", padx=25, pady=(15, 10))

        nav_row = ctk.CTkFrame(self, fg_color="transparent")
        nav_row.pack(fill="x", padx=30, pady=(0, 20))
        ctk.CTkButton(nav_row, text="← Skip", height=38, corner_radius=10,
                      fg_color=COLORS["card_light"], hover_color=COLORS["border"],
                      command=self._skip_question).pack(side="left")
        self.next_btn = ctk.CTkButton(
            nav_row, text="Next Question →", height=38, corner_radius=10,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            command=self._next_question, state="disabled"
        )
        self.next_btn.pack(side="right")

    def _load_question(self):
        self.answer_box.delete("1.0", "end")
        self.model_label.configure(text="")
        self.next_btn.configure(state="disabled")
        self.submit_btn.configure(state="normal")

        idx = self.order[self.current]
        q = HR_QUESTIONS[idx]
        self.question_label.configure(text=q["q"])
        self.counter_label.configure(
            text=f"Question {self.current + 1} of {len(self.order)}")

    def _submit_answer(self):
        idx = self.order[self.current]
        q = HR_QUESTIONS[idx]
        user_answer = self.answer_box.get("1.0", "end").strip()

        self.model_label.configure(text=f"💡 Model Answer:\n{q['model']}")
        self.submit_btn.configure(state="disabled")
        self.next_btn.configure(state="normal")

        self.session_log.append({
            "question": q["q"],
            "user_answer": user_answer,
            "model_answer": q["model"],
        })

    def _skip_question(self):
        self._advance()

    def _next_question(self):
        self._advance()

    def _advance(self):
        if self.current < len(self.order) - 1:
            self.current += 1
            self._load_question()
        else:
            save_json_report("hr_session", {"answers": self.session_log})
            self.question_label.configure(text="🎉 You've completed all HR questions for this session!")
            self.answer_box.pack_forget()
            self.submit_btn.pack_forget()
            self.model_label.configure(text="Great job practicing! Visit Results to see your overall performance.")
            self.next_btn.configure(state="disabled")
