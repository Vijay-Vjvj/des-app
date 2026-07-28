"""
quiz.py
Technical Quiz module: choose a topic, answer 20 MCQs, see correct/wrong
answers and a final score + percentage.
"""

import random

import customtkinter as ctk

from utils import COLORS, FONT_FAMILY, save_json_report, grade_from_percentage
from data.quiz_bank import QUIZ_BANK, TOPICS, QUESTIONS_PER_QUIZ


class QuizFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=COLORS["background"])
        self.app = app
        self.questions = []
        self.current_index = 0
        self.selected_option = ctk.IntVar(value=-1)
        self.answers = []  # list of dicts: question, chosen, correct, is_correct
        self.topic = None

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)

        self._build_topic_selection()

    # ------------------------------------------------------------------
    def _clear(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ------------------------------------------------------------------
    def _build_topic_selection(self):
        self._clear()
        ctk.CTkLabel(
            self.container, text="🧠 Technical Quiz",
            font=(FONT_FAMILY, 26, "bold"), text_color=COLORS["text"]
        ).pack(anchor="w", padx=30, pady=(25, 5))

        ctk.CTkLabel(
            self.container, text="Choose a topic to start a 20-question quiz.",
            font=(FONT_FAMILY, 14), text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=30, pady=(0, 20))

        grid = ctk.CTkFrame(self.container, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=30)

        for i, topic in enumerate(TOPICS):
            card = ctk.CTkFrame(grid, fg_color=COLORS["card"], corner_radius=14)
            card.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky="nsew")
            grid.grid_columnconfigure(i % 3, weight=1)

            ctk.CTkLabel(card, text=topic, font=(FONT_FAMILY, 16, "bold"),
                         text_color=COLORS["text"]).pack(padx=20, pady=(20, 5))
            ctk.CTkLabel(card, text=f"{len(QUIZ_BANK[topic])} questions available",
                         font=(FONT_FAMILY, 11), text_color=COLORS["text_muted"]).pack(pady=(0, 15))
            ctk.CTkButton(
                card, text="Start Quiz", corner_radius=10, height=36,
                fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                command=lambda t=topic: self.start_quiz(t)
            ).pack(padx=20, pady=(0, 20))

    # ------------------------------------------------------------------
    def start_quiz(self, topic):
        self.topic = topic
        bank = QUIZ_BANK[topic]
        if len(bank) >= QUESTIONS_PER_QUIZ:
            self.questions = random.sample(bank, QUESTIONS_PER_QUIZ)
        else:
            # Sample with replacement if the bank has fewer questions
            self.questions = [random.choice(bank) for _ in range(QUESTIONS_PER_QUIZ)]
        self.current_index = 0
        self.answers = []
        self._show_question()

    def _show_question(self):
        self._clear()
        q = self.questions[self.current_index]
        self.selected_option.set(-1)

        top_row = ctk.CTkFrame(self.container, fg_color="transparent")
        top_row.pack(fill="x", padx=30, pady=(25, 5))
        ctk.CTkLabel(
            top_row, text=f"{self.topic} Quiz — Question {self.current_index + 1}/{len(self.questions)}",
            font=(FONT_FAMILY, 18, "bold"), text_color=COLORS["text"]
        ).pack(side="left")

        progress = ctk.CTkProgressBar(self.container, progress_color=COLORS["accent"], height=10)
        progress.pack(fill="x", padx=30, pady=(0, 20))
        progress.set((self.current_index) / len(self.questions))

        card = ctk.CTkFrame(self.container, fg_color=COLORS["card"], corner_radius=14)
        card.pack(fill="both", expand=True, padx=30, pady=10)

        ctk.CTkLabel(
            card, text=q["q"], font=(FONT_FAMILY, 16, "bold"), text_color=COLORS["text"],
            wraplength=700, justify="left"
        ).pack(anchor="w", padx=25, pady=(25, 15))

        for i, option in enumerate(q["options"]):
            ctk.CTkRadioButton(
                card, text=option, variable=self.selected_option, value=i,
                font=(FONT_FAMILY, 13), text_color=COLORS["text"],
                fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"]
            ).pack(anchor="w", padx=35, pady=8)

        nav_row = ctk.CTkFrame(self.container, fg_color="transparent")
        nav_row.pack(fill="x", padx=30, pady=20)

        is_last = self.current_index == len(self.questions) - 1
        ctk.CTkButton(
            nav_row, text="Submit Quiz" if is_last else "Next Question →",
            height=42, corner_radius=10, fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"], command=self._next_question
        ).pack(side="right")

    def _next_question(self):
        q = self.questions[self.current_index]
        chosen = self.selected_option.get()
        is_correct = chosen == q["answer"]
        self.answers.append({
            "question": q["q"],
            "options": q["options"],
            "chosen_index": chosen,
            "correct_index": q["answer"],
            "is_correct": is_correct,
        })

        if self.current_index < len(self.questions) - 1:
            self.current_index += 1
            self._show_question()
        else:
            self._show_results()

    def _show_results(self):
        self._clear()
        correct_count = sum(1 for a in self.answers if a["is_correct"])
        total = len(self.answers)
        percentage = (correct_count / total) * 100 if total else 0
        grade = grade_from_percentage(percentage)

        self.app.session_data["quiz_score"] = percentage

        ctk.CTkLabel(
            self.container, text="📊 Quiz Results", font=(FONT_FAMILY, 24, "bold"),
            text_color=COLORS["text"]
        ).pack(anchor="w", padx=30, pady=(25, 10))

        summary_card = ctk.CTkFrame(self.container, fg_color=COLORS["card"], corner_radius=14)
        summary_card.pack(fill="x", padx=30, pady=10)

        ctk.CTkLabel(
            summary_card, text=f"{self.topic} — {correct_count}/{total} Correct",
            font=(FONT_FAMILY, 18, "bold"), text_color=COLORS["accent"]
        ).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(
            summary_card, text=f"Percentage: {percentage:.1f}%   |   Grade: {grade}",
            font=(FONT_FAMILY, 15), text_color=COLORS["text"]
        ).pack(anchor="w", padx=20, pady=(0, 15))
        pb = ctk.CTkProgressBar(summary_card, progress_color=COLORS["accent"], height=14)
        pb.pack(fill="x", padx=20, pady=(0, 20))
        pb.set(percentage / 100)

        details_frame = ctk.CTkScrollableFrame(self.container, fg_color="transparent", height=280)
        details_frame.pack(fill="both", expand=True, padx=30, pady=10)

        for i, a in enumerate(self.answers, start=1):
            row = ctk.CTkFrame(details_frame, fg_color=COLORS["card"], corner_radius=10)
            row.pack(fill="x", pady=5)
            color = COLORS["accent"] if a["is_correct"] else COLORS["danger"]
            icon = "✅" if a["is_correct"] else "❌"
            ctk.CTkLabel(row, text=f"{icon} Q{i}: {a['question']}", font=(FONT_FAMILY, 12, "bold"),
                         text_color=COLORS["text"], wraplength=650, justify="left").pack(anchor="w", padx=15, pady=(10, 3))
            chosen_text = a["options"][a["chosen_index"]] if 0 <= a["chosen_index"] < len(a["options"]) else "No answer"
            correct_text = a["options"][a["correct_index"]]
            ctk.CTkLabel(row, text=f"Your answer: {chosen_text}", font=(FONT_FAMILY, 11),
                         text_color=color).pack(anchor="w", padx=15)
            if not a["is_correct"]:
                ctk.CTkLabel(row, text=f"Correct answer: {correct_text}", font=(FONT_FAMILY, 11),
                             text_color=COLORS["accent"]).pack(anchor="w", padx=15, pady=(0, 10))
            else:
                ctk.CTkFrame(row, fg_color="transparent", height=8).pack()

        btn_row = ctk.CTkFrame(self.container, fg_color="transparent")
        btn_row.pack(fill="x", padx=30, pady=15)
        ctk.CTkButton(btn_row, text="Retake / Choose Another Topic", height=40, corner_radius=10,
                      fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
                      command=self._build_topic_selection).pack(side="left")

        save_json_report("quiz_report", {
            "topic": self.topic,
            "correct": correct_count,
            "total": total,
            "percentage": percentage,
            "grade": grade,
            "answers": self.answers,
        })
