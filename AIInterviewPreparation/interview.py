"""
interview.py
AI Mock Interview module: presents interview questions one at a time
(randomized each session), lets the user type an answer OR use the
microphone button for a voice answer (speech-to-text), gives a lightweight
offline evaluation, and tracks a communication score.
"""

import random

import customtkinter as ctk

from utils import COLORS, FONT_FAMILY, save_json_report, load_settings
from data.interview_bank import MOCK_INTERVIEW_QUESTIONS, EVALUATION_KEYWORDS
from speech import SpeechRecognizer


def evaluate_answer(text: str):
    """Very lightweight, fully-offline heuristic evaluation of an answer:
    scores length, and presence of positive keywords vs filler words."""
    if not text or not text.strip():
        return 0, ["No answer was provided."]

    words = text.lower().split()
    word_count = len(words)
    feedback = []

    length_score = min(40, word_count * 1.5)
    if word_count < 15:
        feedback.append("Try to elaborate more — aim for at least 30-40 words.")

    positive_hits = sum(1 for kw in EVALUATION_KEYWORDS["positive"] if kw in text.lower())
    keyword_score = min(40, positive_hits * 8)
    if positive_hits == 0:
        feedback.append("Include specific examples or achievements to strengthen your answer.")

    filler_hits = sum(text.lower().count(f) for f in EVALUATION_KEYWORDS["filler"])
    filler_penalty = min(20, filler_hits * 5)
    if filler_hits > 0:
        feedback.append("Reduce filler words (um, like, actually) for clearer communication.")

    structure_score = 20 if any(p in text for p in [".", ","]) else 5
    if structure_score < 20:
        feedback.append("Structure your answer into complete sentences.")

    total = max(0, min(100, length_score + keyword_score + structure_score - filler_penalty))
    if not feedback:
        feedback.append("Well-structured and detailed answer!")
    return round(total), feedback


class InterviewFrame(ctk.CTkFrame):
    def __init__(self, master, app):
        super().__init__(master, fg_color=COLORS["background"])
        self.app = app
        self.recognizer = SpeechRecognizer()
        self.questions = random.sample(
            MOCK_INTERVIEW_QUESTIONS, k=min(8, len(MOCK_INTERVIEW_QUESTIONS))
        )
        self.current = 0
        self.session_log = []
        self._build_ui()
        self._load_question()

    def _build_ui(self):
        header_row = ctk.CTkFrame(self, fg_color="transparent")
        header_row.pack(fill="x", padx=30, pady=(25, 5))
        ctk.CTkLabel(
            header_row, text="🎤 AI Mock Interview",
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
        self.answer_box.pack(fill="x", padx=25, pady=(0, 10))

        mic_row = ctk.CTkFrame(self.card, fg_color="transparent")
        mic_row.pack(fill="x", padx=25, pady=(0, 15))

        self.mic_btn = ctk.CTkButton(
            mic_row, text="🎙  Answer by Voice", height=38, corner_radius=10,
            fg_color=COLORS["secondary"], hover_color=COLORS["primary_hover"],
            command=self._start_voice_answer
        )
        self.mic_btn.pack(side="left")

        self.mic_status = ctk.CTkLabel(
            mic_row, text="", font=(FONT_FAMILY, 12), text_color=COLORS["text_muted"]
        )
        self.mic_status.pack(side="left", padx=15)

        self.submit_btn = ctk.CTkButton(
            self.card, text="Evaluate Answer", height=40, corner_radius=10,
            fg_color=COLORS["primary"], hover_color=COLORS["primary_hover"],
            command=self._submit_answer
        )
        self.submit_btn.pack(anchor="w", padx=25)

        self.feedback_label = ctk.CTkLabel(
            self.card, text="", font=(FONT_FAMILY, 13), text_color=COLORS["accent"],
            wraplength=750, justify="left"
        )
        self.feedback_label.pack(anchor="w", padx=25, pady=(15, 10))

        nav_row = ctk.CTkFrame(self, fg_color="transparent")
        nav_row.pack(fill="x", padx=30, pady=(0, 20))
        self.next_btn = ctk.CTkButton(
            nav_row, text="Next Question →", height=38, corner_radius=10,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            command=self._next_question, state="disabled"
        )
        self.next_btn.pack(side="right")
        ctk.CTkButton(
            nav_row, text="🔀 New Random Question Set", height=38, corner_radius=10,
            fg_color=COLORS["card_light"], hover_color=COLORS["border"],
            command=self._restart
        ).pack(side="left")

    def _restart(self):
        self.questions = random.sample(
            MOCK_INTERVIEW_QUESTIONS, k=min(8, len(MOCK_INTERVIEW_QUESTIONS))
        )
        self.current = 0
        self.session_log = []
        self._load_question()

    def _load_question(self):
        self.answer_box.delete("1.0", "end")
        self.feedback_label.configure(text="")
        self.mic_status.configure(text="")
        self.next_btn.configure(state="disabled")
        self.submit_btn.configure(state="normal")
        q = self.questions[self.current]
        self.question_label.configure(text=q)
        self.counter_label.configure(text=f"Question {self.current + 1} of {len(self.questions)}")

    def _start_voice_answer(self):
        settings = load_settings()
        if not settings.get("voice_enabled", True):
            self.mic_status.configure(text="Voice is disabled in Settings.")
            return

        if not self.recognizer.available:
            self.mic_status.configure(
                text="Speech recognition not installed (pip install SpeechRecognition pyaudio pocketsphinx)."
            )
            return

        self.mic_status.configure(text="🎙 Listening... speak now.")
        self.mic_btn.configure(state="disabled")

        self.recognizer.listen_and_transcribe_async(
            on_result=self._on_voice_result,
            on_error=self._on_voice_error,
        )

    def _on_voice_result(self, text):
        self.after(0, self._apply_voice_result, text)

    def _on_voice_error(self, message):
        self.after(0, self._apply_voice_error, message)

    def _apply_voice_result(self, text):
        self.mic_btn.configure(state="normal")
        self.mic_status.configure(text="Recognized speech inserted below ✅")
        self.answer_box.delete("1.0", "end")
        self.answer_box.insert("1.0", text)

    def _apply_voice_error(self, message):
        self.mic_btn.configure(state="normal")
        self.mic_status.configure(text=message)

    def _submit_answer(self):
        answer_text = self.answer_box.get("1.0", "end").strip()
        score, feedback = evaluate_answer(answer_text)

        self.feedback_label.configure(
            text=f"Communication Score: {score}/100\n" + "\n".join(f"• {f}" for f in feedback)
        )
        self.submit_btn.configure(state="disabled")
        self.next_btn.configure(state="normal")

        self.session_log.append({
            "question": self.questions[self.current],
            "answer": answer_text,
            "score": score,
            "feedback": feedback,
        })

    def _next_question(self):
        if self.current < len(self.questions) - 1:
            self.current += 1
            self._load_question()
        else:
            self._finish_session()

    def _finish_session(self):
        if self.session_log:
            avg_score = sum(item["score"] for item in self.session_log) / len(self.session_log)
        else:
            avg_score = 0
        self.app.session_data["interview_score"] = avg_score
        self.app.session_data["communication_score"] = avg_score

        save_json_report("interview_session", {
            "average_score": avg_score,
            "answers": self.session_log,
        })

        self.question_label.configure(
            text=f"🎉 Interview session complete! Average communication score: {avg_score:.1f}/100"
        )
        self.answer_box.pack_forget()
        self.mic_btn.pack_forget()
        self.submit_btn.pack_forget()
        self.feedback_label.configure(text="Head to Results to see your full performance report.")
        self.next_btn.configure(state="disabled")
